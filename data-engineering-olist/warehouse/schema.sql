CREATE SCHEMA IF NOT EXISTS olist;

CREATE TABLE IF NOT EXISTS olist.fact_orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    customer_unique_id TEXT,
    customer_city TEXT,
    customer_state TEXT,
    seller_id TEXT,
    product_id TEXT,
    product_category_name_english TEXT,
    total_order_value DOUBLE PRECISION,
    delivery_days DOUBLE PRECISION,
    review_score_avg DOUBLE PRECISION,
    monthly_revenue DOUBLE PRECISION,
    customer_lifetime_value DOUBLE PRECISION,
    order_year INT,
    order_month INT
);

CREATE TABLE IF NOT EXISTS olist.dim_customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE IF NOT EXISTS olist.dim_products (
    product_id TEXT PRIMARY KEY,
    product_category_name_english TEXT
);

CREATE TABLE IF NOT EXISTS olist.dim_sellers (
    seller_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS olist.dim_dates (
    order_year INT,
    order_month INT,
    PRIMARY KEY (order_year, order_month)
);
