"""
build_database.py
------------------
Loads the CSVs in /data into a SQLite database (retail.db) so the
project can be explored with pure SQL (as well as pandas).

Run: python3 scripts/build_database.py
"""
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/retail.db")

customers_df = pd.read_csv("data/customers.csv")
products_df = pd.read_csv("data/products.csv")
orders_df = pd.read_csv("data/orders.csv")
order_items_df = pd.read_csv("data/order_items.csv")

customers_df.to_sql("customers", conn, if_exists="replace", index=False)
products_df.to_sql("products", conn, if_exists="replace", index=False)
orders_df.to_sql("orders", conn, if_exists="replace", index=False)
order_items_df.to_sql("order_items", conn, if_exists="replace", index=False)

conn.commit()
print("retail.db built successfully with tables: customers, products, orders, order_items")
conn.close()
