import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    # update database values?
    with db.engine.begin() as connection:
            #get original vals
            result = connection.execute(sqlalchemy.text("SELECT num_red_ml, gold FROM global_inventory"))
            first_row = result.first()

            gold_available = first_row.gold
            red_ml = first_row.num_red_ml

            #update value
            for barrel in barrels_delivered:
                red_ml += barrel.ml_per_barrel * barrel.quantity
                gold_available -= barrel.price * barrel.quantity

            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :red_ml"))
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :gold_available"))
        
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    barrels_to_purchace = 0
    
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT num_red_potions, gold FROM global_inventory"))
            first_row = result.first()

            red_potions = first_row.num_red_potions
            gold_available = first_row.gold
            
            # check if less than ten, is so, buy barrel
    if (red_potions < 10):
        #buy a barrel based on price and how much gold you have
        for barrel in wholesale_catalog:
             if (gold_available >= barrel.price * barrel.quantity):
                  
                  barrels_to_purchase += barrel.quantity
                  break

   
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": barrels_to_purchase,
        }
    ]     

    

    
