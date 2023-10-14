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

    # sum of potions calculated with python syntax
    red_ml_used = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
    green_ml_used = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
    blue_ml_used = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
    dark_used = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)

    print("red used: ", red_ml_used, " green used: ", green_ml_used, " blue used: ", blue_ml_used, "dark used: ", dark_used)

    # process: once potions are delivered, update the database values
    with db.engine.begin() as connection:
            
            for potion in potions_delivered:
                print(potion)
                connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = num_potions + :quantity WHERE type = :potion_type"), {"quantity": potion.quantity, "potion_type": potion.potion_type})


            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :red_ml_used, num_green_ml = num_green_ml - :green_ml_used, num_blue_ml = num_blue_ml - :blue_ml_used"), {"red_ml_used": red_ml_used, "green_ml_used": green_ml_used, "blue_ml_used": blue_ml_used})


    return "OK"
 
# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    bottles = []

    with db.engine.begin() as connection:
            global_inventory_result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))

            first_row = global_inventory_result.first()
            red_ml = first_row.num_red_ml
            green_ml = first_row.num_green_ml
            blue_ml = first_row.num_blue_ml
            
            potions_result = connection.execute(sqlalchemy.text("SELECT type FROM potions ORDER BY num_potions"))

            # potential approach, bottle until youve made 5 (initially just to stock all)
            for potion in potions_result:
                bottled = 0

                while(bottled < 5 and red_ml >= potion.type[0] and green_ml >= potion.type[1] and blue_ml >= potion.type[2]):
                    bottled += 1
                    # subtract from available ml in inventory
                    red_ml -= potion.type[0]
                    green_ml -= potion.type[1]
                    blue_ml -= potion.type[2]

                if bottled > 0:
                    #print("adding sku: ", potion.sku, "amount: ", bottled)
                    bottle = {
                        "potion_type": potion.type,
                        "quantity": bottled
                    }

                    bottles.append(bottle)


    print("BOTTLER/PLAN: result of bottling: ")
    print(bottles)
    return bottles

    