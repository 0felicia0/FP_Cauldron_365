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
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            
            first_row = result.first()

            red_potions = first_row.num_red_potions
            red_ml = first_row.num_red_ml

            green_potions = first_row.num_green_potions
            green_ml = first_row.num_green_ml

            blue_potions = first_row.num_blue_potions
            blue_ml = first_row.num_blue_ml

            # will probably have to adapt to different potion types (colors)
            for p in potions_delivered:
                if p.potion_type == [100, 0, 0, 0]:
                    print("BOTTLER/DELIVER: adding to red")
                    red_potions += p.quantity
                    red_ml -= 100*p.quantity
                if p.potion_type == [0, 100, 0, 0]:
                    print("BOTTLER/DELIVER: adding to green")
                    green_potions += p.quantity
                    green_ml -= 100*p.quantity
                if p.potion_type == [0, 0, 100, 0]:
                    print("BOTTLER/DELIVER: adding to blue")
                    blue_potions += p.quantity
                    blue_ml -= 100*p.quantity

            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_potions, num_red_ml = :red_ml, num_green_potions = :green_potions, num_green_ml = :green_ml, num_blue_potions = :blue_potions, num_blue_ml = :blue_ml"), {"red_potions": red_potions, "red_ml": red_ml, "green_potions": green_potions, "green_ml": green_ml, "blue_potions": blue_potions, "blue_ml": blue_ml})

            print("IN BOTTLER - red potion inventory after delivery: ", red_potions)
            print("IN BOTTLER - green potion inventory after delivery: ", green_potions)
            print("IN BOTTLER - blue potion inventory after delivery: ", blue_potions)

    return "OK"
 
# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

            first_row = result.first()

            red_ml = first_row.num_red_ml
            green_ml = first_row.num_green_ml
            blue_ml = first_row.num_blue_ml
    
    bottles = []
    # every 100ml is a bottle of potion
    red_bottles = red_ml // 100
    green_bottles = green_ml // 100
    blue_bottles = blue_ml // 100

    print("IN BOTTLER - red potions expected to make: ", red_bottles)
    print("IN BOTTLER - green potions expected to make: ", green_bottles)
    print("IN BOTTLER - blue potions expected to make: ", blue_bottles)

    if red_bottles != 0:
         print("adding red to bottles list")
         red = {
            "potion_type": [100, 0, 0, 0],
            "quantity": red_bottles, 
         }

         bottles.append(red)

    if green_bottles != 0:
         green = {
            "potion_type": [0, 100, 0, 0],
            "quantity": green_bottles, 
         }

         bottles.append(green)

    if blue_bottles != 0:
         blue = {
            "potion_type": [0, 0, 100, 0],
            "quantity": blue_bottles, 
         }

         bottles.append(blue)

    print("BOTTLER/PLAN: result of bottling: ")
    print(bottles)
    return bottles

    