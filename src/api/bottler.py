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

                description = "Adding potion: " + str(potion.potion_type) + " quantity: " + str(potion.quantity)

                transaction_id = connection.execute(sqlalchemy.text("""
                                                                INSERT INTO transactions (description)
                                                                VALUES (:description)
                                                                RETURNING transaction_id
                                                                """), {"description": description}).scalar()
                
                connection.execute(sqlalchemy.text("""
                                                    INSERT INTO potion_ledger (change, transaction_id, potion_id)
                                                    SELECT :change, :transaction_id, potion_id 
                                                    FROM potions
                                                    WHERE potions.type = :potion_type
                                                    """), {"change": potion.quantity, "transaction_id": transaction_id, "potion_type": potion.potion_type})
                
                #connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = num_potions + :quantity WHERE type = :potion_type"), {"quantity": potion.quantity, "potion_type": potion.potion_type})

            description = "Subtraction ml after bottling: red: " + str(red_ml_used) + " green: " + str(green_ml_used) + " blue: " + str(blue_ml_used)

            transaction_id = connection.execute(sqlalchemy.text("""
                                                INSERT INTO transactions (description)
                                                VALUES (:description)
                                                RETURNING transaction_id
                                                """), {"description": description}).scalar()
            
            connection.execute(sqlalchemy.text("""
                                                    INSERT INTO ml_ledger (transaction_id, red_ml_change, green_ml_change, blue_ml_change)
                                                    VALUES (:transaction_id, :red_ml_change, :green_ml_change, :blue_ml_change)
                                                    """), {"transaction_id": transaction_id, "red_ml_change": -red_ml_used, "green_ml_change": -green_ml_used, "blue_ml_change": -blue_ml_used})
            
            #connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :red_ml_used, num_green_ml = num_green_ml - :green_ml_used, num_blue_ml = num_blue_ml - :blue_ml_used"), {"red_ml_used": red_ml_used, "green_ml_used": green_ml_used, "blue_ml_used": blue_ml_used})


    return "OK"
 
# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    bottles = []

    with db.engine.begin() as connection:
            #result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))
            ml_result = connection.execute(sqlalchemy.text("""
                                                        SELECT SUM(red_ml_change) AS red_ml, SUM(green_ml_change) AS green_ml, SUM(blue_ml_change) AS blue_ml
                                                        FROM ml_ledger
                                                        """))

            first_row = ml_result.first()
            red_ml = first_row.red_ml
            green_ml = first_row.green_ml
            blue_ml = first_row.blue_ml
            
            potions_result = connection.execute(sqlalchemy.text("SELECT type FROM potions"))

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

    