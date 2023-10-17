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

            description = "initial values after reset"
            transaction_id = connection.execute(sqlalchemy.text("INSERT INTO transactions (description) VALUES (:description) RETURNING transaction_id"), {"description": description}).scalar()

            connection.execute(sqlalchemy.text("INSERT INTO gold_ledger (change, transaction_id) VALUES (100, :transaction_id)"), {"transaction_id": transaction_id})
            connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (transaction_id, red_ml_change, green_ml_change, blue_ml_change) VALUES (:transaction_id, 0, 0, 0)"), {"transaction_id": transaction_id})
            for i in range(1, 8):
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledger (change, transaction_id, potion_id) VALUES (0, :transaction_id, :potion_id)"), {"transaction_id": transaction_id, "potion_id": i})       
            
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Felicia's Potion Shop",
        "shop_owner": "Felicia Patel",
    }

