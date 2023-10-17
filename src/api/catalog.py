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
            # what i want to do: get all potions that have quantity greater than zero
            # need info from potions table where the SUM(change) > 0 and potion.potion_id = potion_ledger.potion_id
            result = connection.execute(sqlalchemy.text("""SELECT sku, name, price, type, SUM(potion_ledger.change) AS quantity 
                                                        FROM potions 
                                                        JOIN potion_ledger ON potions.potion_id = potion_ledger.potion_id
                                                        GROUP BY potions.potion_id
                                                        HAVING SUM(potion_ledger.change) > 0"""))

            for row in result:
                #print(row)
                potion = {
                      "sku": row.sku,
                      "name": row.name,
                      "quantity": row.quantity,
                      "price": row.price,
                      "potion_type": row.type,
                }

                catalog.append(potion)
    print(catalog)
    return catalog           

    

    