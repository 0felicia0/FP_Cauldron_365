import sqlalchemy
from src import database as db

from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    catalog = []

    with db.engine.begin() as connection:
            # grab all rows with available potions
            result = connection.execute(sqlalchemy.text("SELECT sku, name, num_potions, price, type FROM potions WHERE num_potions > 0"))

            for row in result:
                potion = {
                    "sku": row.sku,
                    "name": row.name,
                    "quantity": row.num_potions,
                    "price": row.price,
                    "potion_type": row.type,
                }

                catalog.append(potion)
    
    return catalog           

    

    