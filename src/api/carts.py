import sqlalchemy
from src import database as db

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

from datetime import datetime

from enum import Enum

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

# class search_sort_options(str, Enum):
#     customer_name = "customer_name"
#     item_sku = "item_sku"
#     line_item_total = "line_item_total"
#     timestamp = "timestamp"

# class search_sort_order(str, Enum):
#     asc = "asc"
#     desc = "desc"   

# @router.get("/search/", tags=["search"])
# def search_orders(
#     customer_name: str = "",
#     potion_sku: str = "",
#     search_page: str = "",
#     sort_col: search_sort_options = search_sort_options.timestamp,
#     sort_order: search_sort_order = search_sort_order.desc,
# ):
#     """
#     Search for cart line items by customer name and/or potion sku.

#     Customer name and potion sku filter to orders that contain the 
#     string (case insensitive). If the filters aren't provided, no
#     filtering occurs on the respective search term.

#     Search page is a cursor for pagination. The response to this
#     search endpoint will return previous or next if there is a
#     previous or next page of results available. The token passed
#     in that search response can be passed in the next search request
#     as search page to get that page of results.

#     Sort col is which column to sort by and sort order is the direction
#     of the search. They default to searching by timestamp of the order
#     in descending order.

#     The response itself contains a previous and next page token (if
#     such pages exist) and the results as an array of line items. Each
#     line item contains the line item id (must be unique), item sku, 
#     customer name, line item total (in gold), and timestamp of the order.
#     Your results must be paginated, the max results you can return at any
#     time is 5 total line items.
#     """

#     # find which attribute to sort by
#     if search_sort_options == search_sort_options.customer_name:
#         order_by = db.customers.c.name
#     elif search_sort_options == search_sort_options.item_sku:
#         order_by = db.potions.c.sku
#     elif search_sort_options == search_sort_options.line_item_total:
#         order_by = db.cart_items.c.quantity
    
#     if search_sort_order == search_sort_order.asc:
#         order_by = order_by.asc()

#     # create a fatty join sequence: tables include customers, potions, cart_items
#     # get all first, then filter
#     stmt = """
#             SELECT customers.name AS name, 
#                    cart_items.quantity AS quantity,
#                    cart_items.created_at AS time 
#                    potions.name AS potion_name, 
#                    potions.price AS price
#             FROM carts
#             JOIN customers ON carts.customer_id == customers.id
#             JOIN cart_items ON cart_id == cart_items.id
#             JOIN potions ON cart_item.id == potions.id
#             """
    
#     with db.engine.begin() as connection:
#             result = connection.execute(sqlalchemy.text(stmt))
    
#     for row in result:
#         print(row)
    

#     # filter only if name parameter is passed

#     # for row in result: format information in json
#     search_res = []
#     return {
#         "previous": "",
#         "next": "",
#         "results": [
#             {
#                 "line_item_id": 1,
#                 "item_sku": "1 oblivion potion",
#                 "customer_name": "Scaramouche",
#                 "line_item_total": 50,
#                 "timestamp": "2021-01-01T00:00:00Z",
#             }
#         ],
#     }

# issue definitely with checking out multiple carts: race condition

class NewCart(BaseModel):
    customer: str

class CartItem(BaseModel):
    quantity: int

class CartCheckout(BaseModel):
    payment: str


@router.post("/")
def create_cart(new_cart: NewCart):

    """ """

    with db.engine.begin() as connection:
            
            result = connection.execute(sqlalchemy.text("INSERT INTO carts RETURNING cart_id"))
            cart_id = result.scalar()

            connection.execute(sqlalchemy.text("INSERT INTO customers (name, cart_id) VALUES (:name, :cart_id)"), {"name": new_cart.customer, "cart_id": cart_id})

    print("customer: ", new_cart.customer, " cart_id: ", cart_id)
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
            connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, quantity, potion_id) SELECT :cart_id, :quantity, potions.potion_id FROM potions WHERE potions.sku = :item_sku"), {"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku})
    
    print("adding to cart: ", item_sku, " quantity: ", cart_item.quantity)       
    return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):

    #plan: get cart items from id, update data base, remove tuple from cart_items
    gold_paid = 0
    potions_bought = 0

    # time and date stuff
    today = datetime.now()
    day_time = today.strftime("%m/%d/%Y %H:%M:%S")

    description = "Cart Checkout @ " + day_time + " cart_id: " + str(cart_id) + " payment: " + cart_checkout.payment

    with db.engine.begin() as connection:
            # objectives: subtract items in the cart from inventory, add gold
            transaction_id = connection.execute(sqlalchemy.text("""
                                                                INSERT INTO transactions (description)
                                                                VALUES (:description)
                                                                RETURNING transaction_id
                                                                """), {"description": description}).scalar()
            
            # change to insert into ledger log
            # insert into ledger the change, trans_id and potion_id of every item in the specified cart
            # need: quantity of each potion bought, id returned for ledger
            
            result = connection.execute(sqlalchemy.text("""
                                                        SELECT quantity, potion_id
                                                        FROM cart_items
                                                        WHERE cart_items.cart_id = :cart_id
                                                        """), {"cart_id": cart_id})
            
            for row in result:
                connection.execute(sqlalchemy.text("""
                                                    INSERT INTO potion_ledger (change, transaction_id, potion_id)
                                                    VALUES (:change, :transaction_id, :potion_id)
                                                    """), {"change": -row.quantity, "transaction_id": transaction_id, "potion_id": row.potion_id})
                
            # get rows with right cart_id, where potion_id = cart_item.potion_is, sum all the values
            result = connection.execute(sqlalchemy.text("SELECT SUM(potions.price * cart_items.quantity) AS gold_paid, SUM(cart_items.quantity) AS potions_bought FROM potions JOIN cart_items ON potions.potion_id = cart_items.potion_id WHERE cart_items.cart_id = :cart_id"), {"cart_id": cart_id})

            first_row = result.first()

            gold_paid = first_row.gold_paid
            potions_bought = first_row.potions_bought

            # update gold in global_inventory
            # change to insert into gold ledger log
            connection.execute(sqlalchemy.text("""INSERT INTO gold_ledger (change, transaction_id)
                                                VALUES (:change, :transaction_id)
                                                """), {"change": gold_paid, "transaction_id": transaction_id})

            # remove tuple from carts, and cart_items associated with it
            #connection.execute(sqlalchemy.text("DELETE FROM cart_items WHERE cart_items.cart_id = :cart_id"), {"cart_id": cart_id})
            #connection.execute(sqlalchemy.text("DELETE FROM carts WHERE cart_id = :cart_id"), {"cart_id": cart_id})

    print("cart_id: ", cart_id,  " bought: ", potions_bought, " and paid: ", gold_paid)        

    return {"total_potions_bought": potions_bought, "total_gold_paid": gold_paid}
