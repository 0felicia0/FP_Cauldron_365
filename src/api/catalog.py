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
            result = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE num_potions > 0"))

            for row in result:
                potion = {
                    "sku": row.sku,
                    "name": row.name,
                    "quantity": row.num_potions,
                    "price": row.price,
                    "potion_type": [row.red_ml, row.green_ml, row.blue_ml, row.dark],
                }

                catalog.append(potion)
            
    return catalog           


# OLD CODE

    # with db.engine.begin() as connection:
    #         # is this an int that's returned?
    #         catalogult = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

    #         first_row = catalogult.first()

    #         red_potions_available = first_row.num_red_potions
    #         green_potions_available = first_row.num_green_potions
    #         blue_potions_available = first_row.num_blue_potions
            
    # Can return a max of 20 items


  

    
    # append to list to return
    # if red_potions_available != 0:
    #     red = {
    #             "sku": "RED_POTION_0",
    #             "name": "red potion",
    #             "quantity": red_potions_available,
    #             "price": 50,
    #             "potion_type": [100, 0, 0, 0], 
    #         }
        
    #     catalog.append(red)

    # if green_potions_available != 0:
    #     green = {
    #             "sku": "GREEN_POTION_0",
    #             "name": "green potion",
    #             "quantity": green_potions_available,
    #             "price": 50,
    #             "potion_type": [0, 100, 0, 0], 
    #         }
        
    #     catalog.append(green)

    # if blue_potions_available != 0:
    #     blue = {
    #             "sku": "BLUE_POTION_0",
    #             "name": "blue potion",
    #             "quantity": blue_potions_available,
    #             "price": 50,
    #             "potion_type": [0, 0, 100, 0], 
    #         }
        
    #     catalog.append(blue)
    
    #return a dictionary or array of dictionary
    

    