"""
eda_analysis.py
----------------
Exploratory Data Analysis + visualizations for the Retail Sales
Analytics project. Reads directly from data/retail.db and saves
chart images to /visuals for use in the README / portfolio.

Run: python3 scripts/eda_analysis.py
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

conn = sqlite3.connect("data/retail.db")

# ---------------------------------------------------------
# 1. Monthly revenue trend
# ---------------------------------------------------------
monthly = pd.read_sql("""
    SELECT strftime('%Y-%m', o.order_date) AS month, SUM(oi.net_sales) AS revenue
    FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY month ORDER BY month
""", conn)

plt.figure(figsize=(10, 5))
plt.plot(monthly["month"], monthly["revenue"], marker="o", color="#2563eb")
plt.xticks(rotation=45)
plt.title("Monthly Revenue Trend (2023–2024)", fontsize=13, fontweight="bold")
plt.ylabel("Revenue ($)")
plt.tight_layout()
plt.savefig("visuals/01_monthly_revenue_trend.png")
plt.close()

# ---------------------------------------------------------
# 2. Revenue by category
# ---------------------------------------------------------
category = pd.read_sql("""
    SELECT p.category, SUM(oi.net_sales) AS revenue
    FROM order_items oi JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category ORDER BY revenue DESC
""", conn)

plt.figure(figsize=(8, 5))
sns.barplot(data=category, x="revenue", y="category", hue="category", palette="Blues_r", legend=False)
plt.title("Revenue by Product Category", fontsize=13, fontweight="bold")
plt.xlabel("Revenue ($)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("visuals/02_revenue_by_category.png")
plt.close()

# ---------------------------------------------------------
# 3. Regional performance
# ---------------------------------------------------------
region = pd.read_sql("""
    SELECT c.region, SUM(oi.net_sales) AS revenue
    FROM orders o JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.region ORDER BY revenue DESC
""", conn)

plt.figure(figsize=(7, 5))
sns.barplot(data=region, x="region", y="revenue", hue="region", palette="viridis", legend=False)
plt.title("Revenue by Region", fontsize=13, fontweight="bold")
plt.ylabel("Revenue ($)")
plt.xlabel("")
plt.tight_layout()
plt.savefig("visuals/03_revenue_by_region.png")
plt.close()

# ---------------------------------------------------------
# 4. Discount vs profit
# ---------------------------------------------------------
disc = pd.read_sql("""
    SELECT discount, AVG(profit) AS avg_profit
    FROM order_items GROUP BY discount ORDER BY discount
""", conn)

plt.figure(figsize=(7, 5))
sns.barplot(data=disc, x="discount", y="avg_profit", hue="discount", palette="rocket", legend=False)
plt.title("Average Profit per Item vs. Discount Level", fontsize=13, fontweight="bold")
plt.xlabel("Discount")
plt.ylabel("Avg Profit ($)")
plt.tight_layout()
plt.savefig("visuals/04_discount_vs_profit.png")
plt.close()

# ---------------------------------------------------------
# 5. Customer segment revenue
# ---------------------------------------------------------
segment = pd.read_sql("""
    SELECT c.segment, SUM(oi.net_sales) AS revenue
    FROM customers c JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.segment ORDER BY revenue DESC
""", conn)

plt.figure(figsize=(7, 7))
plt.pie(segment["revenue"], labels=segment["segment"], autopct="%1.1f%%",
        colors=sns.color_palette("Set2"), startangle=90)
plt.title("Revenue Share by Customer Segment", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("visuals/05_segment_revenue_share.png")
plt.close()

# ---------------------------------------------------------
# 6. Top 10 products
# ---------------------------------------------------------
top_products = pd.read_sql("""
    SELECT p.product_name, SUM(oi.net_sales) AS revenue
    FROM order_items oi JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_id ORDER BY revenue DESC LIMIT 10
""", conn)

plt.figure(figsize=(9, 6))
sns.barplot(data=top_products, x="revenue", y="product_name", hue="product_name", palette="mako", legend=False)
plt.title("Top 10 Products by Revenue", fontsize=13, fontweight="bold")
plt.xlabel("Revenue ($)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("visuals/06_top10_products.png")
plt.close()

conn.close()
print("EDA complete. 6 charts saved to /visuals")
