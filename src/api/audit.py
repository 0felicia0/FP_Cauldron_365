import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
            # is this an int that's returned?
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

            first_row = result.first()

            gold = first_row.gold

            red_potions = first_row.num_red_potions
            red_ml = first_row.num_red_ml

            green_potions = first_row.num_green_potions
            green_ml = first_row.num_green_ml

            blue_potions = first_row.num_blue_potions
            blue_ml = first_row.num_blue_ml


    return {"number_of_red_ potions": red_potions, "red_ml_in_barrels": red_ml, "number_of_green_potions": green_potions, "green_ml_in_barrels": green_ml, "number_of_blue_potions": blue_potions, "blue_ml_in_barrels": blue_ml, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
