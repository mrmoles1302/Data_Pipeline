-- Revenue by month
SELECT order_year, order_month, SUM(monthly_revenue) AS revenue
FROM olist.fact_orders
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

-- Top categories
SELECT product_category_name_english, COUNT(*) AS orders
FROM olist.fact_orders
GROUP BY product_category_name_english
ORDER BY orders DESC;

-- Repeat customers
SELECT customer_unique_id, COUNT(*) AS orders
FROM olist.fact_orders
GROUP BY customer_unique_id
HAVING COUNT(*) > 1
ORDER BY orders DESC;

-- Seller performance
SELECT seller_id, SUM(monthly_revenue) AS revenue
FROM olist.fact_orders
GROUP BY seller_id
ORDER BY revenue DESC;

-- Delivery analysis
SELECT order_year, order_month, AVG(delivery_days) AS avg_delivery_days
FROM olist.fact_orders
GROUP BY order_year, order_month
ORDER BY order_year, order_month;
