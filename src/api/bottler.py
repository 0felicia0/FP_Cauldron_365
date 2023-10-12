import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

# every alternate tick provides an opportunity to make potions

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)

    # process: once potions are delivered, update the database values
    with db.engine.begin() as connection:
            
            #connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = potions.num_potions - :quantity WHERE potions.red_ml = :potion_type[0] AND potions.green_ml = :potion_type[1] AND potions.blue_ml = :potion_type[2] AND potions.dark = :potion_type[3]"))

            result = connection.execute(sqlalchemy.text("SELECT * FROM potions"))
            result_list = list(result)
            # sum of potions calculated with python syntax
            

            red_ml_used = 0
            green_ml_used = 0
            blue_ml_used = 0

            for potion in potions_delivered:
                print(potion)
                potions_to_add = 0
                for row in result_list:
                    red_ml = row.red_ml
                    green_ml = row.green_ml
                    blue_ml = row.blue_ml
                    dark = row.dark

                    row_potion_mix = [red_ml, green_ml, blue_ml, dark]

                    print("potion.potion_type: ", potion.potion_type)
                    print("row mix: ", row_potion_mix)

                    if potion.potion_type == row_potion_mix:
                        print("current inventory of sku: ", row.sku, "inventory: ", row.num_potions)

                        potions_to_add += potion.quantity

                        red_ml_used += row.red_ml * potion.quantity
                        green_ml_used += row.green_ml * potion.quantity
                        blue_ml_used += row.blue_ml * potion.quantity
                        
                        connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = num_potions + :potions_to_add WHERE red_ml = :red_ml AND green_ml = :green_ml AND blue_ml = :blue_ml AND dark = :dark"), {"potions_to_add": potions_to_add, "potion_type": potion.potion_type, "red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark": dark})

                        print("resulting potion number: sku: ", row.sku, "potions_to_add: ", potions_to_add)
            print("red used: ", red_ml_used, " green used: ", green_ml_used, " blue used: ", blue_ml_used)
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :red_ml_used, num_green_ml = num_green_ml - :green_ml_used, num_blue_ml = num_blue_ml - :blue_ml_used"), {"red_ml_used": red_ml_used, "green_ml_used": green_ml_used, "blue_ml_used": blue_ml_used})


    return "OK"
 
# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    bottles = []

    with db.engine.begin() as connection:
            global_inventory_result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

            first_row = global_inventory_result.first()
            red_ml = first_row.num_red_ml
            green_ml = first_row.num_green_ml
            blue_ml = first_row.num_blue_ml
            
            potions_result = connection.execute(sqlalchemy.text("SELECT * FROM potions"))

            # potential approach, bottle until youve made 5 (initially just to stock all)
            for potion in potions_result:
                bottled = 0

                while(bottled < 5 and red_ml >= potion.red_ml and green_ml >= potion.green_ml and blue_ml >= potion.blue_ml):
                    bottled += 1
                    # subtract from available ml in inventory
                    red_ml -= potion.red_ml
                    green_ml -= potion.green_ml
                    blue_ml -= potion.blue_ml

                if bottled > 0:
                    print("adding sku: ", potion.sku, "amount: ", bottled)
                    bottle = {
                        "potion_type": [potion.red_ml, potion.green_ml, potion.blue_ml, potion.dark],
                        "quantity": bottled
                    }

                    bottles.append(bottle)


    print("BOTTLER/PLAN: result of bottling: ")
    print(bottles)
    return bottles

    