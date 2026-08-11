/* ============================================================
   RETAIL SALES ANALYTICS — BUSINESS QUESTION QUERIES
   Database: data/retail.db (SQLite)
   Tables: customers, products, orders, order_items
   ============================================================ */


-- 1. Total revenue, total profit, and profit margin overall
SELECT
    ROUND(SUM(net_sales), 2)  AS total_revenue,
    ROUND(SUM(profit), 2)     AS total_profit,
    ROUND(SUM(profit) * 100.0 / SUM(net_sales), 2) AS profit_margin_pct
FROM order_items;


-- 2. Monthly revenue trend (find seasonality / growth patterns)
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    ROUND(SUM(oi.net_sales), 2)     AS revenue,
    COUNT(DISTINCT o.order_id)      AS num_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;


-- 3. Top 10 best-selling products by revenue
SELECT
    p.product_name,
    p.category,
    ROUND(SUM(oi.net_sales), 2) AS revenue,
    SUM(oi.quantity)            AS units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;


-- 4. Revenue and profit margin by category
SELECT
    p.category,
    ROUND(SUM(oi.net_sales), 2) AS revenue,
    ROUND(SUM(oi.profit), 2)    AS profit,
    ROUND(SUM(oi.profit) * 100.0 / SUM(oi.net_sales), 2) AS margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;


-- 5. Regional performance — revenue by region
SELECT
    c.region,
    ROUND(SUM(oi.net_sales), 2) AS revenue,
    COUNT(DISTINCT o.order_id)  AS num_orders,
    ROUND(SUM(oi.net_sales) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.region
ORDER BY revenue DESC;


-- 6. Customer segment analysis (Consumer / Corporate / Home Office)
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id) AS num_customers,
    ROUND(SUM(oi.net_sales), 2)   AS revenue,
    ROUND(SUM(oi.net_sales) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.segment
ORDER BY revenue DESC;


-- 7. Top 10 customers by lifetime value (LTV)
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    ROUND(SUM(oi.net_sales), 2) AS lifetime_value,
    COUNT(DISTINCT o.order_id)  AS num_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id
ORDER BY lifetime_value DESC
LIMIT 10;


-- 8. RFM-style analysis — customers who haven't ordered recently (churn risk)
-- "Recency" = days since last order, relative to the most recent date in the dataset
WITH last_order AS (
    SELECT customer_id, MAX(order_date) AS last_order_date
    FROM orders
    GROUP BY customer_id
),
max_date AS (
    SELECT MAX(order_date) AS dataset_max_date FROM orders
)
SELECT
    lo.customer_id,
    c.customer_name,
    lo.last_order_date,
    CAST(julianday((SELECT dataset_max_date FROM max_date)) - julianday(lo.last_order_date) AS INTEGER) AS days_since_last_order
FROM last_order lo
JOIN customers c ON lo.customer_id = c.customer_id
ORDER BY days_since_last_order DESC
LIMIT 20;


-- 9. Discount impact on profit — does higher discount hurt margins?
SELECT
    discount,
    COUNT(*)                     AS num_line_items,
    ROUND(SUM(net_sales), 2)     AS revenue,
    ROUND(SUM(profit), 2)        AS profit,
    ROUND(AVG(profit), 2)        AS avg_profit_per_item
FROM order_items
GROUP BY discount
ORDER BY discount;


-- 10. Shipping mode analysis — usage and average order value
SELECT
    o.ship_mode,
    COUNT(*) AS num_orders,
    ROUND(AVG(o.order_total), 2) AS avg_order_value,
    ROUND(AVG(julianday(o.ship_date) - julianday(o.order_date)), 1) AS avg_ship_days
FROM orders o
GROUP BY o.ship_mode
ORDER BY num_orders DESC;


-- 11. Month-over-month revenue growth %
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        SUM(oi.net_sales) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month), 2) AS mom_growth_pct
FROM monthly
ORDER BY month;


-- 12. New vs. repeat customer revenue split (per month, based on signup_date)
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    CASE WHEN strftime('%Y-%m', c.signup_date) = strftime('%Y-%m', o.order_date)
         THEN 'New Customer' ELSE 'Repeat Customer' END AS customer_type,
    ROUND(SUM(oi.net_sales), 2) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month, customer_type
ORDER BY month, customer_type;
