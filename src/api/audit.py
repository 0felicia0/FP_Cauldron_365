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

    return {"number_of_potions": red_potions, "ml_in_barrels": red_ml, "gold": gold}

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
