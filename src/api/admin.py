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
            # reset ledgers and transaction             
            connection.execute(sqlalchemy.text("TRUNCATE potion_ledger"))
            connection.execute(sqlalchemy.text("TRUNCATE gold_ledger"))
            connection.execute(sqlalchemy.text("TRUNCATE ml_ledger"))
            connection.execute(sqlalchemy.text("TRUNCATE transactions"))
            # reset carts and cart_items too
            connection.execute(sqlalchemy.text("TRUNCATE carts CASCADE"))

            connection.execute(sqlalchemy.text("INSERT INTO gold_ledger (change) VALUES (100)"))       
            
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Felicia's Potion Shop",
        "shop_owner": "Felicia Patel",
    }

