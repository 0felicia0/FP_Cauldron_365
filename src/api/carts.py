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

customers = []
cart_id_gen = 0

class NewCart(BaseModel):
    customer: str

class CartItem(BaseModel):
    quantity: int

class Cart:
     def __init__(self, cart_identification, cart, items):
        
        self.cart_identification = cart_identification
        self.cart = cart
        self.items = items

@router.post("/")
def create_cart(new_cart: NewCart):

    """ """
    global cart_id_gen
    cart = Cart(cart_id_gen, new_cart, None)

    customers.append(cart)
    cart_id_gen+=1

    # cart_id is defined as a string in API Specs
    return {"cart_id": cart_id_gen - 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    if cart_id < len(customers):
        return customers[cart_id]
    else:
        return {"error": "Cart not found"}



@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    customer = get_cart(cart_id)
    customer.items = cart_item

    return "OK"


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT gold, num_red_potions FROM global_inventory"))

            first_row = result.first()
            gold_available = first_row.gold
            red_potions = first_row.num_red_potions

            #add gold from purchase, subtract potions bought
            #check here how many in database left
            customer = get_cart(cart_id)
            if customer.items.quantity <= red_potions:
                #can buy
                bought = customer.items.quantity
                red_potions -= bought
                paid = customer.items.quantity * 50
                gold_available += paid
            
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_potions, gold = :gold_available"), {"red_potions": red_potions, "gold_available": gold_available})
    
    return {"total_potions_bought": bought, "total_gold_paid": paid}

    