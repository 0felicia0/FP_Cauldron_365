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

# issue definitely with checking out multiple carts: race condition

class NewCart(BaseModel):
    customer: str

class CartItem(BaseModel):
    quantity: int

class CartCheckout(BaseModel):
    payment: str

# class Cart:
#      def __init__(self, cart_identification, customer):
#         self.customer = customer
#         self.cart_identification = cart_identification
#         self.items = []

# class Item:
#     def __init__(self, sku, quantity):
#         self.sku = sku
#         self.quantity = quantity

@router.post("/")
def create_cart(new_cart: NewCart):

    """ """

    with db.engine.begin() as connection:
            cart_id = connection.execute(sqlalchemy.text("INSERT INTO carts (customer) VALUES (:customer_name) RETURNING cart_id"), {"customer_name": new_cart.customer})

    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """NEVER GETS CALLED"""
    
    return

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """"""
    # change to reflect lecture notes
    with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, potion_id, quantity) SELECT :cart_id, :quantity, potions.potion_id FROM potions WHERE potions.sku = :item_sku"), {"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku})
           
    return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):

    """
    UPDATE potions
    SET num_potions = potions.num_potions - cart_items.quantity
    FROM cart_items
    WHERE potion.id = cart_items.potion_id and cart_items.cart_id = :cart_id;
    """
    #plan: get cart items from id, update data base, remove tuple from cart_items
    gold_paid = 0
    potions_bought = 0

    with db.engine.begin() as connection:
            # objectives: subtract items in the cart from inventory, add gold
            
            connection.execute(sqlalchemy.text("UPDATE potions SET num_potions = potions.num_potions - cart_items.quantity FROM cart_items WHERE potions.potion_id = cart_items.potion_id AND cart_items.cart_id = :cart_id"), {"cart_id": cart_id})
    
            # get rows with right cart_id, where potion_id = cart_item.potion_is, sum all the values
            result = connection.execute(sqlalchemy.text("SELECT SUM(potions.price * cart_item.quantity) AS gold_paid, SUM(cart_items.quatity) AS potions_bought FROM potions JOIN cart_items ON potions.potion_id = cart_items.potion_id WHERE cart_items.cart_id = :cart_id"), {"cart_id": cart_id})
    
            gold_paid = result.gold_paid
            potions_bought = result.potions_bought

            #remove tuple from carts

    return {"total_potions_bought": potions_bought, "total_gold_paid": gold_paid}
