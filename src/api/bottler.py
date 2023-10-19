import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
from datetime import date
from datetime import datetime


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
    dark_ml_used = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)

    print("red used: ", red_ml_used, " green used: ", green_ml_used, " blue used: ", blue_ml_used, "dark used: ", dark_ml_used)

    
    # process: once potions are delivered, update the database values
    # think about how you want to read the transaction logs and work from there

    # time and date stuff
    today = datetime.utcnow()
    day_time = today.strftime("%m/%d/%Y %H:%M:%S")

    description = "Delivering potions @ " + day_time

    with db.engine.begin() as connection:
            
            transaction_id = connection.execute(sqlalchemy.text("""
                                                                INSERT INTO transactions (description)
                                                                VALUES (:description)
                                                                RETURNING transaction_id
                                                                """), {"description": description}).scalar()            

            for potion in potions_delivered:
                print(potion)

                connection.execute(sqlalchemy.text("""
                                                    INSERT INTO potion_ledger (change, transaction_id, potion_id)
                                                    SELECT :change, :transaction_id, potion_id 
                                                    FROM potions
                                                    WHERE potions.type = :potion_type
                                                    """), {"change": potion.quantity, "transaction_id": transaction_id, "potion_type": potion.potion_type})
                
            
            connection.execute(sqlalchemy.text("""
                                                INSERT INTO ml_ledger (transaction_id, red_ml_change, green_ml_change, blue_ml_change, dark_ml_change)
                                                VALUES (:transaction_id, :red_ml_change, :green_ml_change, :blue_ml_change, :dark_ml_change)
                                                """), 
                                                {"transaction_id": transaction_id, 
                                                 "red_ml_change": -red_ml_used, 
                                                 "green_ml_change": -green_ml_used, 
                                                 "blue_ml_change": -blue_ml_used,
                                                 "dark_ml_change": -dark_ml_used})
            
    return "OK"
 
# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    
    """
    #DONT BOTTLE MORE THAN 300 FOR INVENTORY!!!!

    bottles = []

    with db.engine.begin() as connection:
            
            # get potions' quantities and types
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT potions.type, SUM(potion_ledger.change) AS quantity
                                                        FROM potions
                                                        JOIN potion_ledger ON potions.potion_id = potion_ledger.potion_id
                                                        GROUP BY potion.type
                                                        """))       
            
            potions = result.fetchall()
            potion_types = len(potions)

            result = connection.execute(sqlalchemy.text("SELECT SUM(change) AS total_potions FROM potion_ledger"))
            first_row = result.first()
            total_potions = first_row.total_potions

            print("potion types: ", potion_types)
            
            # get available ml
            ml = connection.execute(sqlalchemy.text("""
                                                    SELECT SUM(red_ml_change) AS red_ml, SUM(green_ml_change) AS green_ml, SUM(blue_ml_change) AS blue_ml, SUM(dark_ml_change) AS dark_ml
                                                    FROM ml_ledger
                                                    """))
            
            ml = ml.first()
            red_ml = ml.red_ml
            green_ml = ml.green_ml
            blue_ml = ml.blue_ml
            dark_ml = ml.dark_ml

            print("in bottler, available mL: red: ", red_ml, " green: ", green_ml, " blue: ", blue_ml, " dark: ", dark_ml)
            
            max_bottles = (red_ml + green_ml + blue_ml + dark_ml) // 100
            
            bottles_per_type = max_bottles//potion_types

            print("max bottles: ", max_bottles," bottles per type: ", bottles_per_type)
            
            for potion in potions:
                print(potion)
                bottled = 0
                while (total_potions < 300 and bottled < bottles_per_type and potion.type[0] <= red_ml and potion.type[1] <= green_ml and potion.type[2] <= blue_ml and potion.type[3] <= dark_ml):
                    red_ml -= potion.type[0]
                    green_ml -= potion.type[1]
                    blue_ml -= potion.type[2]
                    dark_ml -= potion.type[3]
                    bottled += 1

                    total_potions += 1
                
                if bottled > 0:
                     bottle = {
                          "potion_type": potion.type,
                          "quantity": bottled
                     }

                     bottles.append(bottle)                
            
    print("BOTTLER/PLAN: result of bottling: ")
    print(bottles)
    return bottles

    