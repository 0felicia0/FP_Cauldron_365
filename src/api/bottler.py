import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

# every alternate tick provides an opportunity to make potions

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
            
            #connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = potions.num_potions - :quantity WHERE potions.red_ml = :potion_type[0] AND potions.green_ml = :potion_type[1] AND potions.blue_ml = :potion_type[2] AND potions.dark = :potion_type[3]"))

            result = connection.execute(sqlalchemy.text("SELECT * FROM potions"))

            # sum of potions calculated with python syntax
            potions_to_add = 0

            for potion in potions_delivered:
               for row in result:
                    if potion.potion_type == [row.red_ml, row.green_ml, row.blue_ml, row.dark]:
                        print("current inventory of sku: ", row.sku, "inventory: ", row.num_potions)

                        potions_to_add += potion.quantity

                        connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = num_potions + :potions_to_add"), {"potions_to_add": potions_to_add})

                        print("resulting potion number: sku: ", row.sku, "potions_to_add: ", potions_to_add)

    return "OK"
 
# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    bottles = []

    with db.engine.begin() as connection:
            global_inventory_result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

            first_row = global_inventory_result.first()
            red_ml = first_row.num_red_ml
            green_ml = first_row.num_green_ml
            blue_ml = first_row.num_blue_ml
            
            potions_result = connection.execute(sqlalchemy.text("SELECT * FROM potions"))

            # potential approach, bottle until youve made 5 (initially just to stock all)
            for potion in potions_result:
                bottled = 0

                while(bottled < 5 and red_ml >= potion.red_ml and green_ml >= potion.green_ml and blue_ml >= potion.blue_ml):
                    bottled += 1
                    # subtract from available ml in inventory
                    red_ml -= potion.red_ml
                    green_ml -= potion.green_ml
                    blue_ml -= potion.blue_ml

                if bottled > 0:
                    print("adding sku: ", potion.sku, "amount: ", bottled)
                    bottle = {
                        "potion_type": [potion.red_ml, potion.green_ml, potion.blue_ml, potion.dark],
                        "quantity": bottled
                    }

                    bottles.append(bottle)


    print("BOTTLER/PLAN: result of bottling: ")
    print(bottles)
    return bottles

    