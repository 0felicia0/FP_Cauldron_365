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
            """
            SELECT sku, name, price, type 
            FROM potions 
            JOIN potion_ledger ON potions.potion_id = potion_ledger.potion_id
            GROUP BY potions.id
            HAVING SUM(potion_ledger.change > 0)
            """
            # grab all rows with available potions
            # what i want to do: get all potions that have quantity greater than zero
            # need info from potions table where the SUM(change) > 0 and potion.potion_id = potion_ledger.potion_id
            result = connection.execute(sqlalchemy.text("""SELECT p.sku, p.name, p.price, p.type 
                                                        FROM potions p
                                                        JOIN potion_ledger pl ON p.id = pl.potion_id
                                                        GROUP BY p.sku, p.name, p.price, p.type
                                                        HAVING SUM(pl.change) > 0"""))
            
            # result = connection.execute(sqlalchemy.text("""SELECT sku, name, num_potions, price, type 
            #                                             FROM potions 
            #                                             WHERE num_potions > 0"""))

            for row in result:
                   print(row)
    #              potion = {
    #                  "sku": row.sku,
    #                  "name": row.name,
    #                  "quantity": row.num_potions,
    #                  "price": row.price,
    #                  "potion_type": row.type,
    #              }

    #              catalog.append(potion)
    
    # return catalog           

    

    