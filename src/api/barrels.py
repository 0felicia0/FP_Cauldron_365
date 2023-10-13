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

    # put variables here, not inside connection
    # for loop out here
    # print results
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    gold = 0
    
    for barrel in barrels_delivered:
            gold += barrel.price * barrel.quantity

            if "RED" in barrel.sku:
                red_ml += barrel.ml_per_barrel * barrel.quantity
                 
            elif "GREEN" in barrel.sku:
                green_ml += barrel.ml_per_barrel * barrel.quantity
                 
            elif "BLUE" in barrel.sku:
                blue_ml += barrel.ml_per_barrel * barrel.quantity
                 
            else: 
                raise Exception("Invalid potion")
             
    print("red_ml: ", red_ml, "green_ml: ", green_ml, "blue_ml: ", blue_ml)

    # update database values?
    with db.engine.begin() as connection:
            # tripe quote syntax
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :red_ml, num_green_ml = num_green_ml + :green_ml, num_blue_ml = num_blue_ml + :blue_ml, gold = gold - :gold"), {"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "gold": gold})
        
    return "OK"

            #get original vals
            # result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")) # this is unecessary, can calculate and add later
            # first_row = result.first()

            # gold_available = first_row.gold
            # red_ml = first_row.num_red_ml
            # green_ml = first_row.num_green_ml
            # blue_ml = first_row.num_blue_ml

            # # could use dictionary

            # #update value
            # for barrel in barrels_delivered:
            #     if "RED" in barrel.sku:
            #         red_ml += barrel.ml_per_barrel * barrel.quantity
            #         gold_available -= barrel.price * barrel.quantity
            #     elif "GREEN" in barrel.sku:
            #         green_ml += barrel.ml_per_barrel * barrel.quantity
            #         gold_available -= barrel.price * barrel.quantity
            #     elif "BLUE" in barrel.sku:
            #         blue_ml += barrel.ml_per_barrel * barrel.quantity
            #         gold_available -= barrel.price * barrel.quantity
            #     else: 
            #         raise Exception("Invalid potion")


            # red_ml = red_ml + :red_ml


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    barrels = [] # list to return
    
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            first_row = result.first()

            gold_available = first_row.gold
            red_ml = first_row.num_red_ml
            green_ml = first_row.num_green_ml
            blue_ml = first_row.num_blue_ml
            
            # logic ideas: if ml < certain amount, try to buy if enough gold
            
            for barrel in wholesale_catalog:
                print(barrel)
                barrels_to_purchase = 0

                if "RED" in barrel.sku: # initial amount of ml less that 1000
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

                elif "GREEN" in barrel.sku:
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

                elif "BLUE" in barrel.sku:
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



# OLD CODE FROM A1

            # if (red_potions < 10):
            #     #buy a barrel based on price and how much gold you have
            #     for barrel in wholesale_catalog:
            #             if barrel.sku == "SMALL_RED_BARREL": #github specs say just to buy small red barrel
            #                 quantity = 0
            #                 while(gold_available >= barrel.price and quantity < barrel.quantity):
            #                     barrels_to_purchase += 1
            #                     quantity += 1
            #                     gold_available -= barrel.price
                            
            #                 # if quantity > 0: add sku to list


    
    

    # return barrels
    #return [
        #{
            #"sku": "SMALL_RED_BARREL", # will probably have to adjust later when we purchase something other than small red barrel
            #"quantity": barrels_to_purchase,
       # }
   # ]     

    

    
