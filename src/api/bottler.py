import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

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
            result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_red_ml FROM global_inventory"))
            
            first_row = result.first()

            red_potions = first_row.num_red_potions
            red_ml = first_row.num_red_ml

            # will probably have to adapt to different potion types (colors)
            for p in potions_delivered:
                red_potions += p.quantity
                red_ml -= 100*p.quantity
                
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_potions, num_red_ml = :red_ml"), {"red_potions": red_potions, "red_ml": red_ml})

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
            result = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))

            first_row = result.first()

            red_ml = first_row.num_red_ml
    
    # every 100ml is a bottle of potion
    num_potions = red_ml // 100

    if num_potions == 0:
         return []

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_potions,
            }
        ]


    