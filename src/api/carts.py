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

# issue definitely with checking out multiple carts

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

class Item:
    def __init__(self, sku, quantity):
        self.sku = sku
        self.quantity = quantity

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
    
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

            first_row = result.first()

            red_potions = first_row.num_red_potions
            green_potions = first_row.num_green_potions
            blue_potions = first_row.num_blue_potions

    if (item_sku == "RED_POTION_0" and red_potions >= cart_item.quantity) or (item_sku == "GREEN_POTION_0" and green_potions >= cart_item.quantity) or (item_sku == "BLUE_POTION_0" and blue_potions >= cart_item.quantity):
        item = Item(item_sku, cart_item.quantity)
        cart.items.append(item)

    else:
        return "insufficient stock - cannot add items to cart"

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
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

            first_row = result.first()
            gold_available = first_row.gold
            red_potions = first_row.num_red_potions
            green_potions = first_row.num_green_potions
            blue_potions = first_row.num_blue_potions

            red_potions_bought = 0
            green_potions_bought = 0
            blue_potions_bought = 0
            #add gold from purchase, subtract potions bought
            #check here how many in database left
            cart = get_cart(cart_id)

            for item in cart.items:
                if "RED" in item.sku and item.quantity <= red_potions:
                    red_potions -= item.quantity
                    red_potions_bought += item.quantity
                    gold_available += item.quantity * 50
                    gold_paid += item.quantity * 50
                if "GREEN" in item.sku and item.quantity <= green_potions:
                    green_potions -= item.quantity
                    green_potions_bought += item.quantity
                    gold_available += item.quantity * 50
                    gold_paid += item.quantity * 50
                if "BLUE" in item.sku and item.quantity <= blue_potions:
                    blue_potions -= item.quantity
                    blue_potions_bought += item.quantity
                    gold_available += item.quantity * 50
                    gold_paid += item.quantity * 50

  
            
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :red_potions, num_green_potions = :green_potions, num_blue_potions = :blue_potions, gold = :gold_available"), {"red_potions": red_potions, "green_potions": green_potions, "blue_potions": blue_potions, "gold_available": gold_available})
    
    carts.pop(cart_id) #remove cart from dictionary bc already processed
   
    print("red bought: ", red_potions_bought)
    print("green bought: ", green_potions_bought)
    print("blue bought: ", blue_potions_bought)
    print("total gold paid: ", gold_paid)
    
    return {"total_potions_bought": red_potions_bought + green_potions_bought + blue_potions_bought, "total_gold_paid": gold_paid}

    