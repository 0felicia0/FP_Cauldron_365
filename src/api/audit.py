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

            result = connection.execute(sqlalchemy.text("SELECT SUM(change) AS total_potions FROM potion_ledger"))
            first_row = result.first()
            total_potions = first_row.total_potions

            result = connection.execute(sqlalchemy.text("SELECT SUM(red_ml_change + green_ml_change + blue_ml_change) AS total_ml FROM ml_ledger"))
            first_row = result.first()
            total_ml = first_row.total_ml

            result = connection.execute(sqlalchemy.text("SELECT SUM(change) AS gold FROM gold_ledger"))
            first_row = result.first()
            gold = first_row.gold

    return {"number_of_potions": total_potions, "ml_in_barrels":  total_ml, "gold": gold}

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
