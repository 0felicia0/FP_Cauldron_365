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
            result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
            num_potions = result.scalar()

            result = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
            num_ml = result.scalar()

            # will probably have to adapt to different potion types (colors)
            for p in potions_delivered:
                 num_potions += p.quantity
                 num_ml -= 100 * p.quantity

            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :num_potions"))
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :num_ml"))

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
            num_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
    
    # every 100ml is a bottle of potion
    num_potions = num_ml // 100

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_potions,
            }
        ]

    