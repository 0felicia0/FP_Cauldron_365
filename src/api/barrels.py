import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from datetime import datetime
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

    # put variables here, not inside connection
    # for loop out here
    # print results
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    gold = 0
    
    for barrel in barrels_delivered:
            gold += barrel.price * barrel.quantity

            if barrel.potion_type == [1, 0, 0, 0]:
                red_ml += barrel.ml_per_barrel * barrel.quantity
                 
            elif barrel.potion_type == [0, 1, 0, 0]:
                green_ml += barrel.ml_per_barrel * barrel.quantity
                 
            elif barrel.potion_type == [0, 0, 1, 0]:
                blue_ml += barrel.ml_per_barrel * barrel.quantity
                 
            else: 
                raise Exception("Invalid potion")
            
    # time and date stuff
    today = datetime.now()
    day_time = today.strftime("%m/%d/%Y %H:%M:%S")
            
    description = "Delivering barrels @ " + day_time + " red_ml: " + str(red_ml) + " green_ml: " + str(green_ml) + " blue_ml: " + str(blue_ml)
             
    print(description)

    # update database values?
    with db.engine.begin() as connection:
            # tripe quote syntax

            # insert a transaction, ml_ledger
            transaction_id = connection.execute(sqlalchemy.text("""INSERT INTO transactions (description) 
                                                                VALUES (:description) 
                                                                RETURNING transaction_id"""), {"description": description}).scalar()
            
            connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (transaction_id, red_ml_change, green_ml_change, blue_ml_change) 
                                               VALUES (:transaction_id, :red_ml, :green_ml, :blue_ml)"""), {"transaction_id": transaction_id, "red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml})

            #connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :red_ml, num_green_ml = num_green_ml + :green_ml, num_blue_ml = num_blue_ml + :blue_ml, gold = gold - :gold"), {"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "gold": gold})
        
    return "OK"



# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    barrels = [] # list to return
    
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
            
            # logic ideas: if ml < certain amount, try to buy if enough gold
            
            for barrel in wholesale_catalog:
                print(barrel)
                barrels_to_purchase = 0

                if barrel.potion_type == [1, 0, 0, 0]: # initial amount of ml less that 1000
                    # buy if gold available and until I buy 1000 ml
                    while red_ml < 500 and gold_available >= barrel.price and barrels_to_purchase < barrel.quantity:
                        barrels_to_purchase += 1
                        red_ml += barrel.ml_per_barrel
                        gold_available -= barrel.price
            

                    if barrels_to_purchase > 0:
                        red = {
                            "sku": barrel.sku,
                            "quantity": barrels_to_purchase
                        }

                        barrels.append(red)

                elif barrel.potion_type == [0, 1, 0, 0]:
                    # buy if gold available and until I buy 1000 ml
                    while green_ml < 500 and gold_available >= barrel.price and barrels_to_purchase < barrel.quantity:
                        barrels_to_purchase += 1
                        green_ml += barrel.ml_per_barrel
                        gold_available -= barrel.price
            
                    if barrels_to_purchase > 0:
                        green = {
                            "sku": barrel.sku,
                            "quantity": barrels_to_purchase
                        }

                        barrels.append(green)

                elif barrel.potion_type == [0, 0, 1, 0]:
                    # buy if gold available and until I buy 1000 ml
                    while blue_ml < 500 and gold_available >= barrel.price and barrels_to_purchase < barrel.quantity:
                        barrels_to_purchase += 1
                        blue_ml += barrel.ml_per_barrel
                        gold_available -= barrel.price
   

                    if barrels_to_purchase > 0:
                        blue = {
                            "sku": barrel.sku,
                            "quantity": barrels_to_purchase
                        }

                        barrels.append(blue)

                 

    print("barrels planning to purchase: ")
    print(barrels)

    print("resulting ml should be: red: ", red_ml, "green: ", green_ml, "blue: ", blue_ml)                     

    return barrels # use same approach as catalog (appending to a list)


    

    
