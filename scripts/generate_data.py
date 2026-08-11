"""
generate_data.py
-----------------
Generates a realistic, internally-consistent retail sales dataset for
the Retail Sales Analytics project.

Creates 4 CSV files in /data:
    customers.csv
    products.csv
    orders.csv
    order_items.csv

Run: python3 scripts/generate_data.py
"""

import numpy as np
import pandas as pd
from faker import Faker
import random

random.seed(42)
np.random.seed(42)
fake = Faker()
Faker.seed(42)

N_CUSTOMERS = 1200
N_PRODUCTS = 150
N_ORDERS = 8000
START_DATE = pd.Timestamp("2023-01-01")
END_DATE = pd.Timestamp("2024-12-31")

REGIONS = ["North", "South", "East", "West", "Central"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
CATEGORIES = {
    "Electronics": ["Headphones", "Smartphone", "Laptop", "Smartwatch", "Tablet", "Camera"],
    "Furniture": ["Office Chair", "Desk", "Bookshelf", "Sofa", "Bed Frame"],
    "Apparel": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Cap"],
    "Home & Kitchen": ["Blender", "Cookware Set", "Vacuum Cleaner", "Air Fryer", "Coffee Maker"],
    "Sports": ["Yoga Mat", "Dumbbells", "Cycling Helmet", "Running Shoes", "Tennis Racket"],
}
SHIP_MODES = ["Standard", "Express", "Same Day"]

# ---------- customers.csv ----------
customers = []
for cid in range(1, N_CUSTOMERS + 1):
    signup_date = fake.date_between(start_date=START_DATE.date(), end_date=END_DATE.date())
    customers.append({
        "customer_id": f"CUST{cid:05d}",
        "customer_name": fake.name(),
        "segment": random.choices(SEGMENTS, weights=[0.6, 0.3, 0.1])[0],
        "region": random.choice(REGIONS),
        "city": fake.city(),
        "signup_date": signup_date,
    })
customers_df = pd.DataFrame(customers)

# ---------- products.csv ----------
products = []
pid = 1
for category, items in CATEGORIES.items():
    for _ in range(N_PRODUCTS // len(CATEGORIES)):
        name = random.choice(items)
        base_price = {
            "Electronics": (50, 1500),
            "Furniture": (80, 900),
            "Apparel": (10, 120),
            "Home & Kitchen": (20, 300),
            "Sports": (15, 250),
        }[category]
        price = round(random.uniform(*base_price), 2)
        cost = round(price * random.uniform(0.5, 0.75), 2)
        products.append({
            "product_id": f"PROD{pid:04d}",
            "product_name": f"{name} {random.choice(['Pro','Lite','Max','Plus','Basic','Elite'])}",
            "category": category,
            "unit_price": price,
            "unit_cost": cost,
        })
        pid += 1
products_df = pd.DataFrame(products)

# ---------- orders.csv & order_items.csv ----------
orders = []
order_items = []
item_id = 1

# give some months seasonal boost (Nov/Dec sales spike - like real retail)
def seasonal_weight(date):
    month = date.month
    if month in (11, 12):
        return 1.8
    if month in (6, 7):
        return 1.3
    return 1.0

date_range = pd.date_range(START_DATE, END_DATE, freq="D")
date_weights = np.array([seasonal_weight(d) for d in date_range])
date_weights = date_weights / date_weights.sum()

for oid in range(1, N_ORDERS + 1):
    order_date = np.random.choice(date_range, p=date_weights)
    order_date = pd.Timestamp(order_date)
    customer = customers_df.sample(1).iloc[0]
    ship_mode = random.choices(SHIP_MODES, weights=[0.6, 0.3, 0.1])[0]
    ship_days = {"Standard": 5, "Express": 2, "Same Day": 0}[ship_mode]
    ship_date = order_date + pd.Timedelta(days=ship_days)

    n_items = random.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
    order_products = products_df.sample(n_items)

    order_total = 0
    for _, prod in order_products.iterrows():
        qty = random.randint(1, 5)
        discount = random.choices([0, 0.05, 0.1, 0.15, 0.2], weights=[0.5, 0.2, 0.15, 0.1, 0.05])[0]
        gross = prod["unit_price"] * qty
        net = round(gross * (1 - discount), 2)
        profit = round(net - (prod["unit_cost"] * qty), 2)
        order_total += net

        order_items.append({
            "order_item_id": item_id,
            "order_id": f"ORD{oid:06d}",
            "product_id": prod["product_id"],
            "quantity": qty,
            "discount": discount,
            "net_sales": net,
            "profit": profit,
        })
        item_id += 1

    orders.append({
        "order_id": f"ORD{oid:06d}",
        "customer_id": customer["customer_id"],
        "order_date": order_date.date(),
        "ship_date": ship_date.date(),
        "ship_mode": ship_mode,
        "order_total": round(order_total, 2),
    })

orders_df = pd.DataFrame(orders)
order_items_df = pd.DataFrame(order_items)

# ---------- save ----------
customers_df.to_csv("data/customers.csv", index=False)
products_df.to_csv("data/products.csv", index=False)
orders_df.to_csv("data/orders.csv", index=False)
order_items_df.to_csv("data/order_items.csv", index=False)

print("Generated:")
print(f"  customers.csv    -> {len(customers_df):,} rows")
print(f"  products.csv     -> {len(products_df):,} rows")
print(f"  orders.csv       -> {len(orders_df):,} rows")
print(f"  order_items.csv  -> {len(order_items_df):,} rows")
