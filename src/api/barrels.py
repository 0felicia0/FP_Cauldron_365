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

    # update database values?
    with db.engine.begin() as connection:
            #get original vals
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            first_row = result.first()

            gold_available = first_row.gold
            red_ml = first_row.num_red_ml
            green_ml = first_row.num_green_ml
            blue_ml = first_row.num_blue_ml

            #update value
            for barrel in barrels_delivered:
                if "RED" in barrel.sku:
                    red_ml += barrel.ml_per_barrel * barrel.quantity
                    gold_available -= barrel.price * barrel.quantity
                if "GREEN" in barrel.sku:
                    green_ml += barrel.ml_per_barrel * barrel.quantity
                    gold_available -= barrel.price * barrel.quantity
                if "BLUE" in barrel.sku:
                    blue_ml += barrel.ml_per_barrel * barrel.quantity
                    gold_available -= barrel.price * barrel.quantity

            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :red_ml, num_green_ml = :green_ml, num_blue_ml = :blue_ml, gold = :gold_available"), {"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "gold_available": gold_available})
        
    return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    barrels = [] # list to return
    
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            first_row = result.first()

            red_potions = first_row.num_red_potions
            green_potions = first_row.num_green_potions
            blue_potions = first_row.num_blue_potions
            gold_available = first_row.gold
            

            # gather all the info for dif barrels and just purchase the best option: max ml for min gold?
            # starter logic: apply same concept as assignment 1 and work from there

            potential_red_potions = 0
            potential_green_potions = 0
            potential_blue_potions = 0

            running_red_ml = 0
            running_green_ml = 0
            running_blue_ml = 0
            

            # current version: just buying one barrel per color -> making sure I have enough gold to purchase more than one color
            for barrel in wholesale_catalog:
                 quantity = 0

                 if "RED" in barrel.sku:
                    if red_potions < 10:
                     
                        while gold_available <= barrel.price and quantity < barrel.quantity and potential_red_potions < 10:
                             quantity += 1
                             running_red_ml += barrel.ml_per_barrel
                             potential_red_potions = running_red_ml//100 # track -> did I already buy enough to make at least ten red (dont over purchase -> save for other colors)
                             gold_available -= barrel.price

                    if quantity > 0:
                         red = {
                            "sku": barrel.sku,
                            "quantity": quantity
                         }
                        
                         print("Buying red barrel")
                         print("SKU: ", barrel.sku)
                         print("QUANTITY BOUGHT: ", quantity)

                         barrels.append(red)
                       
                 elif "GREEN" in barrel.sku:
                    if green_potions < 10:
                     
                        while gold_available <= barrel.price and quantity < barrel.quantity and potential_green_potions < 10:
                             quantity += 1
                             running_green_ml += barrel.ml_per_barrel
                             potential_green_potions = running_green_ml//100
                             gold_available -= barrel.price

                    if quantity > 0:
                         green = {
                            "sku": barrel.sku,
                            "quantity": quantity
                         }

                         print("Buying green barrel")
                         print("SKU: ", barrel.sku)
                         print("QUANTITY BOUGHT: ", quantity)

                         barrels.append(green)

                 elif "BLUE" in barrel.sku:
                    if blue_potions < 10:
                     
                        while gold_available <= barrel.price and quantity < barrel.quantity and potential_blue_potions < 10:
                             quantity += 1
                             running_blue_ml += barrel.ml_per_barrel
                             potential_blue_potions = running_blue_ml//100
                             gold_available -= barrel.price

                    if quantity > 0:
                         blue = {
                            "sku": barrel.sku,
                            "quantity": quantity
                         }

                         print("Buying blue barrel")
                         print("SKU: ", barrel.sku)
                         print("QUANTITY BOUGHT: ", quantity)

                         barrels.append(blue)

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

    

    
