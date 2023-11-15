import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

# every 12th tick presents an opportunity to buy a barrel

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0
    gold = 0
    
    for barrel in barrels_delivered:
            gold += barrel.price * barrel.quantity

            if barrel.potion_type == [1, 0, 0, 0]:
                red_ml += barrel.ml_per_barrel * barrel.quantity
                 
            elif barrel.potion_type == [0, 1, 0, 0]:
                green_ml += barrel.ml_per_barrel * barrel.quantity
                 
            elif barrel.potion_type == [0, 0, 1, 0]:
                blue_ml += barrel.ml_per_barrel * barrel.quantity

            elif barrel.potion_type == [0, 0, 0, 1]:
                dark_ml += barrel.ml_per_barrel * barrel.quantity     
            else: 
                raise Exception("Invalid potion")
            
            
    description = "Delivering barrels: "+ " red_ml: " + str(red_ml) + " green_ml: " + str(green_ml) + " blue_ml: " + str(blue_ml) + " dark_ml: " + str(dark_ml)
             
    print(description)

    # update database values?
    with db.engine.begin() as connection:
            # tripe quote syntax

            # insert a transaction, ml_ledger
            transaction_id = connection.execute(sqlalchemy.text("""INSERT INTO transactions (description) 
                                                                VALUES (:description) 
                                                                RETURNING transaction_id"""), {"description": description}).scalar()
            
            connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (transaction_id, red_ml_change, green_ml_change, blue_ml_change, dark_ml_change) 
                                               VALUES (:transaction_id, :red_ml, :green_ml, :blue_ml, :dark_ml)"""), {"transaction_id": transaction_id, "red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml})


            connection.execute(sqlalchemy.text("""
                                                INSERT INTO gold_ledger (change, transaction_id)
                                                VALUES (:gold, :transaction_id)
                                                 """), {"gold": -gold, "transaction_id": transaction_id})
        
    return "OK" 



# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    # potential plan: if 300 in inventory already, dont buy
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("""SELECT SUM(red_ml_change) AS red_ml, SUM(green_ml_change) AS green_ml, SUM(blue_ml_change) AS blue_ml 
                                                        FROM ml_ledger"""))
            first_row = result.first()

            red_ml = first_row.red_ml
            green_ml = first_row.green_ml
            blue_ml = first_row.blue_ml
            print("IN BARRELS PLAN, ml in inventory: red: ", red_ml, " green: ", green_ml, " blue: ", blue_ml)
    
   
            result = connection.execute(sqlalchemy.text("""SELECT SUM(change) AS gold
                                                        FROM gold_ledger""")) 
            
            first_row = result.first()
            gold_available = first_row.gold
            print("IN BARRELS PLAN, gold: ", gold_available)


            result = connection.execute(sqlalchemy.text("""SELECT SUM(change) AS total_potions
                                                        FROM potion_ledger""")) 
            
            first_row = result.first()
            total_potions = first_row.total_potions
            print("IN BARRELS PLAN, potions in inventory: ", total_potions) 

    barrels = [] # list to return

    total_ml = red_ml + green_ml + blue_ml

    potential_potions = total_ml // 100
    total_potions += potential_potions

    potions_to_make = 300 - total_potions

    ml_to_buy = potions_to_make * 100

    red_to_buy = (ml_to_buy // 3)
    green_to_buy = (ml_to_buy // 3) 
    blue_to_buy = (ml_to_buy // 3) 

 # adjust if needed
    #red_to_buy = 10000
    #green_to_buy = 9000
    #blue_to_buy = 20000
    

    print("total_potions: ", total_potions, " potions to make: ", potions_to_make, " ml_to_buy: ", ml_to_buy, " ml_per_color: ", red_to_buy)

    #if total_potions < 300:
    for barrel in wholesale_catalog:
            print(barrel)
            barrels_to_purchase = 0

            if barrel.potion_type == [1, 0, 0, 0]: # initial amount of ml less that 1000
                # buy if gold available and until I buy 1000 ml
                while red_to_buy > 0 and gold_available >= barrel.price and barrels_to_purchase < barrel.quantity:
                    barrels_to_purchase += 1
                    #red_ml += barrel.ml_per_barrel
                    gold_available -= barrel.price
                    red_to_buy -= barrel.ml_per_barrel

            elif barrel.potion_type == [0, 1, 0, 0]:
                # buy if gold available and until I buy 1000 ml
                while green_to_buy > 0 and gold_available >= barrel.price and barrels_to_purchase < barrel.quantity:
                    barrels_to_purchase += 1
                    #green_ml += barrel.ml_per_barrel
                    gold_available -= barrel.price
                    green_to_buy -= barrel.ml_per_barrel

            elif barrel.potion_type == [0, 0, 1, 0]:
                # buy if gold available and until I buy 1000 ml
                while blue_to_buy > 0 and gold_available >= barrel.price and barrels_to_purchase < barrel.quantity:
                    barrels_to_purchase += 1
                    #blue_ml += barrel.ml_per_barrel
                    gold_available -= barrel.price
                    blue_to_buy -= barrel.ml_per_barrel
            # dark
            elif barrel.potion_type == [0, 0, 0, 1] and gold_available >= barrel.price:
                # buy if gold available and until I buy 1000 ml
                barrels_to_purchase += 1
                gold_available -= barrel.price

            if barrels_to_purchase > 0:
                barrel = {
                    "sku": barrel.sku,
                    "quantity": barrels_to_purchase
                }

                barrels.append(barrel) 

    print("barrels planning to purchase: ")
    print(barrels)

    return barrels # use same approach as catalog (appending to a list)



    

    
