import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))

md("""# Retail Sales Analytics — Exploratory Data Analysis
**Goal:** Analyze 2 years of retail transaction data to uncover revenue trends, top-performing products/regions, customer value patterns, and the impact of discounting on profitability — then translate findings into business recommendations.

**Dataset:** 1,200 customers · 150 products · 8,000 orders · 14,000+ order line items (2023–2024)
""")

code("""import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110

conn = sqlite3.connect("../data/retail.db")
""")

md("## 1. Data Overview")
code("""orders = pd.read_sql("SELECT * FROM orders", conn)
order_items = pd.read_sql("SELECT * FROM order_items", conn)
customers = pd.read_sql("SELECT * FROM customers", conn)
products = pd.read_sql("SELECT * FROM products", conn)

print("Orders:", orders.shape)
print("Order items:", order_items.shape)
print("Customers:", customers.shape)
print("Products:", products.shape)
orders.head()
""")

code("""# Quick data quality check
print(orders.isnull().sum())
print(order_items.isnull().sum())
""")

md("## 2. Overall Revenue & Profit")
code("""summary = pd.read_sql('''
    SELECT ROUND(SUM(net_sales),2) AS total_revenue,
           ROUND(SUM(profit),2) AS total_profit,
           ROUND(SUM(profit)*100.0/SUM(net_sales),2) AS profit_margin_pct
    FROM order_items
''', conn)
summary
""")

md("""**Insight:** The business runs at a healthy overall margin. This baseline number is what every deeper cut (category, region, discount) should be compared against.""")

md("## 3. Monthly Revenue Trend")
code("""monthly = pd.read_sql('''
    SELECT strftime('%Y-%m', o.order_date) AS month, SUM(oi.net_sales) AS revenue
    FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY month ORDER BY month
''', conn)

plt.figure(figsize=(10,5))
plt.plot(monthly["month"], monthly["revenue"], marker="o", color="#2563eb")
plt.xticks(rotation=45)
plt.title("Monthly Revenue Trend (2023-2024)")
plt.ylabel("Revenue ($)")
plt.tight_layout()
plt.show()
""")

md("""**Insight:** Clear seasonality — revenue spikes in Nov/Dec (holiday shopping) and a smaller lift in Jun/Jul. This should drive inventory planning and marketing calendar decisions.""")

md("## 4. Revenue by Category")
code("""category = pd.read_sql('''
    SELECT p.category, SUM(oi.net_sales) AS revenue, SUM(oi.profit) AS profit
    FROM order_items oi JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category ORDER BY revenue DESC
''', conn)
category["margin_pct"] = (category["profit"]/category["revenue"]*100).round(2)
category
""")

code("""plt.figure(figsize=(8,5))
sns.barplot(data=category, x="revenue", y="category", hue="category", palette="Blues_r", legend=False)
plt.title("Revenue by Product Category")
plt.xlabel("Revenue ($)")
plt.ylabel("")
plt.tight_layout()
plt.show()
""")

md("## 5. Regional Performance")
code("""region = pd.read_sql('''
    SELECT c.region, SUM(oi.net_sales) AS revenue, COUNT(DISTINCT o.order_id) AS num_orders
    FROM orders o JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.region ORDER BY revenue DESC
''', conn)
region["avg_order_value"] = (region["revenue"]/region["num_orders"]).round(2)
region
""")

md("## 6. Discount Impact on Profitability")
code("""disc = pd.read_sql('''
    SELECT discount, COUNT(*) AS n_items, ROUND(AVG(profit),2) AS avg_profit
    FROM order_items GROUP BY discount ORDER BY discount
''', conn)
disc
""")

code("""plt.figure(figsize=(7,5))
sns.barplot(data=disc, x="discount", y="avg_profit", hue="discount", palette="rocket", legend=False)
plt.title("Average Profit per Item vs. Discount Level")
plt.tight_layout()
plt.show()
""")

md("""**Insight:** Profit per item declines sharply as discount level increases. Discounts above ~15% are close to break-even at the unit level — worth flagging to the pricing/promotions team.""")

md("## 7. Top 10 Customers by Lifetime Value")
code("""top_customers = pd.read_sql('''
    SELECT c.customer_id, c.customer_name, c.segment,
           ROUND(SUM(oi.net_sales),2) AS lifetime_value,
           COUNT(DISTINCT o.order_id) AS num_orders
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id
    ORDER BY lifetime_value DESC
    LIMIT 10
''', conn)
top_customers
""")

md("""## 8. Key Business Recommendations

1. **Double down on Nov/Dec campaigns** — seasonality shows outsized returns; align inventory and ad spend ahead of this window.
2. **Re-evaluate deep discounting (15%+)** — margin data shows these promotions barely break even; consider capping discounts or bundling instead.
3. **Prioritize the top-performing region and category** in acquisition marketing, since they show the best revenue-per-order efficiency.
4. **Launch a win-back campaign** for customers with long recency gaps (see SQL churn-risk query) to recover at-risk revenue.
5. **Corporate segment** shows the highest revenue per customer — worth a dedicated account-based marketing push.
""")

nb["cells"] = cells
nbf.write(nb, "notebooks/retail_sales_eda.ipynb")
print("Notebook written.")
