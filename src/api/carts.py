import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

customers = {}
cart_id = 0

class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):

    """ """

    customers[cart_id] = new_cart
    cart_id+=1

    # cart_id is defined as a string in API Specs
    return {"cart_id": cart_id - 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return {customers[cart_id]}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    # based off of the sku, update the amount that the customer wants to purchase
    return "OK"


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT gold, num_red_potions FROM golbal_inventory"))

            first_row = result.first()
            gold_available = first_row.gold
            red_potions = first_row.num_red_potions

            #add gold from purchase, subtract potions bought
    
    return {"total_potions_bought": 1, "total_gold_paid": 50}

    