import sqlalchemy
from src import database as db

from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    with db.engine.begin() as connection:
            # is this an int that's returned?
            result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))

            first_row = result.first()

            red_potions_available = first_row.num_red_potions
            
    # Can return a max of 20 items

    if (red_potions_available == 0):
          # return empty array if 0 potions available
          return []

    #return a dictionary or array of dictionary
    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": red_potions_available,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]

    