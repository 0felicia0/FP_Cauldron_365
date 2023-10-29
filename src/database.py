import os
import dotenv
from sqlalchemy import create_engine
import sqlalchemy

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

metadata_obj = sqlalchemy.MetaData()
potions = sqlalchemy.Table("potions", metadata_obj, autoload_with=engine)
potion_ledger = sqlalchemy.Table("potion_ledger", metadata_obj, autoload_with=engine)
gold_ledger = sqlalchemy.Table("gold_ledger", metadata_obj, autoload_with=engine)
ml_ledger = sqlalchemy.Table("ml_ledger", metadata_obj, autoload_with=engine)
carts = sqlalchemy.Table("carts", metadata_obj, autoload_with=engine)
cart_items = sqlalchemy.Table("cart_items", metadata_obj, autoload_with=engine)
transactions = sqlalchemy.Table("transactions", metadata_obj, autoload_with=engine)
customers = sqlalchemy.Table("customers", metadata_obj, autoload_with=engine)