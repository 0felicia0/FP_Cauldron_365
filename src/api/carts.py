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

carts = {}
cart_id_gen = 0

class NewCart(BaseModel):
    customer: str

class CartItem(BaseModel):
    quantity: int

class Cart:
     def __init__(self, cart_identification, customer):
        self.customer = customer
        self.cart_identification = cart_identification
        self.items = []

@router.post("/")
def create_cart(new_cart: NewCart):

    """ """
    global cart_id_gen
    cart = Cart(cart_id_gen, new_cart.customer)

    carts[cart.cart_identification] = cart
    cart_id_gen += 1

    return {"cart_id": cart.cart_identification}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    cart = carts.get(cart_id)# get cart from dictionary

    if cart is None:
        return {"error": "cart not found"}
    
    return cart

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    # this one go crazy
    cart = get_cart(cart_id)

    #testing purposes
    if cart is None:
        return {"error": "cart not found"} 
    
    cart.items.append(cart_item)

    return "OK"


class CartCheckout(BaseModel):
    payment: str


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):

    """ """
    items_bought = 0
    gold_paid = 0

    print(cart_checkout.payment)

    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT gold, num_red_potions FROM global_inventory"))

            first_row = result.first()
            gold_available = first_row.gold
            red_potions = first_row.num_red_potions

            #add gold from purchase, subtract potions bought
            #check here how many in database left
            cart = get_cart(cart_id)
            
            for item in cart.items:
                if item.quantity <= red_potions:
                    red_potions -= item.quantity
                    items_bought += item.quantity
                    gold_available += item.quantity * 50
                    gold_paid += item.quantity * 50
            
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_potions, gold = :gold_available"), {"red_potions": red_potions, "gold_available": gold_available})
    
    carts.pop(cart_id) #remove cart from dictionary bc already processed
    
    return {"total_potions_bought": items_bought, "total_gold_paid": gold_paid}

    