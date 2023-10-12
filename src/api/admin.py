import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
            # is this an int that's returned?
            result = connection.execute(sqlalchemy.text("SELECT * FROM potions"))

            for row in result:
                connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = 0"))

            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")) 

            first_row = result.first()
            connection.execute(sqlalchemy.text("UPDATE potions SET total_potions = 0, num_red_ml = 0, num_green_ml = 0, num_blue_ml = 0, gold = 100"))       
            
                            

    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Potion Shop",
        "shop_owner": "Potion Seller",
    }

