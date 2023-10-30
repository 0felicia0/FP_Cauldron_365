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

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   



@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

     # stmt = """
    #         SELECT customers.name AS name, 
    #                cart_items.quantity AS quantity,
    #                cart_items.created_at AS time, 
    #                potions.sku AS sku, 
    #                potions.price AS price
    #         FROM carts
    #         JOIN customers ON carts.customer_id = customers.id
    #         JOIN cart_items ON carts.cart_id = cart_items.cart_id
    #         JOIN potions ON cart_items.potion_id = potions.potion_id
    #         """
    
    #find which attribute to sort by
    if search_sort_options == search_sort_options.customer_name:
        order_by = db.customers.c.name
    elif search_sort_options == search_sort_options.item_sku:
        order_by = db.potions.c.sku
    elif search_sort_options == search_sort_options.line_item_total:
        order_by = db.cart_items.c.quantity
    else:
        order_by = db.cart_items.c.created_at
         
    if search_sort_order == search_sort_order.asc:
        order_by = order_by.asc()
    else:
        order_by = order_by.desc()

    # create a fatty join sequence: tables include customers, potions, cart_items
    # get all first, then filter
   
    
    stmt = (sqlalchemy.select(db.customers.c.name, 
                             db.cart_items.c.quantity.label("quantity"), 
                             db.transactions.c.created_at.label("time"),
                             db.potions.c.sku.label("sku"),
                             db.potions.c.potion_id.label("potion_id"),
                             db.cart_items.c.current_price.label("price") 
                             ).select_from(db.carts
                             .join(db.customers, db.carts.c.customer_id == db.customers.c.id)
                             .join(db.cart_items, db.cart_items.c.cart_id == db.carts.c.cart_id)
                             .join(db.potions, db.potions.c.potion_id == db.cart_items.c.potion_id)
                             .join(db.transactions, db.transactions.c.cart_id == db.carts.c.cart_id)
                             )
                             .order_by(order_by)
                             )
    
    # filter only if name parameter is passed
    if customer_name != "":
        stmt = stmt.where(db.customers.c.name.ilike(f"%{customer_name}%"))
    # filter only if name parameter is passed
    if potion_sku != "":
        stmt = stmt.where(db.potions.c.sku.ilike(f"%{potion_sku}%"))

    search_res = []
    
    with db.engine.begin() as connection:
            result = connection.execute(stmt)
            line_item_id = 1
            for row in result:
                search_res.append(  
                                    {
                                        "line_item_id": line_item_id,
                                        "item_sku": str(row.quantity) + " " + row.sku,
                                        "customer_name": row.name,
                                        "line_item_total": row.quantity * row.price,
                                        "timestamp": row.time,
                                    }
                                )
                
                line_item_id += 1
    

    

    # for row in result: format information in json
    return {
         "previous": "", 
         "next": "",
         "results": search_res
    }

    # return {
    #     "previous": "",
    #     "next": "",
    #     "results": [
    #         {
    #             "line_item_id": 1,
    #             "item_sku": "1 oblivion potion",
    #             "customer_name": "Scaramouche",
    #             "line_item_total": 50,
    #             "timestamp": "2021-01-01T00:00:00Z",
    #         }
    #     ],
    # }

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
            
            result = connection.execute(sqlalchemy.text("""INSERT INTO customers (name)
                                                            VALUES (:name)
                                                            ON CONFLICT (name) DO UPDATE
                                                            SET name = EXCLUDED.name
                                                            RETURNING id;"""), {"name": new_cart.customer})
            customer_id = result.scalar()

            result = connection.execute(sqlalchemy.text("INSERT INTO carts (customer_id) VALUES (:customer_id) RETURNING cart_id"), {"customer_id": customer_id})
            cart_id = result.scalar()

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
            connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, quantity, potion_id, current_price) SELECT :cart_id, :quantity, potions.potion_id, potions.price FROM potions WHERE potions.sku = :item_sku"), {"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku})
    
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

    #description = "Cart Checkout @ " + day_time + " cart_id: " + str(cart_id) + " payment: " + cart_checkout.payment
    description = "test"

    with db.engine.begin() as connection:
            # objectives: subtract items in the cart from inventory, add gold
            transaction_id = connection.execute(sqlalchemy.text("""
                                                                INSERT INTO transactions (description, cart_id)
                                                                VALUES (:description, :cart_id)
                                                                RETURNING transaction_id
                                                                """), {"description": description, "cart_id": cart_id}).scalar()
            
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
