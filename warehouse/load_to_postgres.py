import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from config.settings import POSTGRES_URL, CURATED_DIR, LOG_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger(__name__)


def load_to_postgres() -> None:
    engine = create_engine(POSTGRES_URL)
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE SCHEMA IF NOT EXISTS olist")

    parquet_path = CURATED_DIR / 'olist_curated.parquet'
    df = pd.read_parquet(parquet_path)

    df['order_id'] = df.get('order_id', pd.Series([f'order_{i}' for i in range(len(df))], index=df.index))
    df['customer_id'] = df.get('customer_id', pd.Series([None] * len(df), index=df.index))
    df['customer_unique_id'] = df.get('customer_unique_id', pd.Series([None] * len(df), index=df.index))
    df['customer_city'] = df.get('customer_city', pd.Series([None] * len(df), index=df.index))
    df['customer_state'] = df.get('customer_state', pd.Series([None] * len(df), index=df.index))
    df['seller_id'] = df.get('seller_id', pd.Series([None] * len(df), index=df.index))
    df['product_id'] = df.get('product_id', pd.Series([None] * len(df), index=df.index))
    df['product_category_name_english'] = df.get('product_category_name_english', pd.Series([None] * len(df), index=df.index))
    df['total_order_value'] = pd.to_numeric(df.get('total_order_value', df.get('monthly_revenue', pd.Series(0.0, index=df.index))), errors='coerce').fillna(0.0)
    df['delivery_days'] = pd.to_numeric(df.get('delivery_days', df.get('avg_delivery_days', pd.Series(0.0, index=df.index))), errors='coerce').fillna(0.0)
    df['review_score_avg'] = pd.to_numeric(df.get('review_score_avg', pd.Series(0.0, index=df.index)), errors='coerce').fillna(0.0)
    df['monthly_revenue'] = pd.to_numeric(df.get('monthly_revenue', pd.Series(0.0, index=df.index)), errors='coerce').fillna(0.0)
    df['customer_lifetime_value'] = pd.to_numeric(df.get('customer_lifetime_value', df.get('monthly_revenue', pd.Series(0.0, index=df.index))), errors='coerce').fillna(0.0)

    fact_orders = df[['order_id', 'customer_id', 'customer_unique_id', 'customer_city', 'customer_state', 'seller_id', 'product_id', 'product_category_name_english', 'total_order_value', 'delivery_days', 'review_score_avg', 'monthly_revenue', 'customer_lifetime_value', 'order_year', 'order_month']].copy()
    fact_orders.to_sql('fact_orders', engine, schema='olist', if_exists='replace', index=False)

    dim_customers = df[['customer_id', 'customer_unique_id', 'customer_city', 'customer_state']].drop_duplicates().copy()
    dim_customers.to_sql('dim_customers', engine, schema='olist', if_exists='replace', index=False)

    dim_products = df[['product_id', 'product_category_name_english']].drop_duplicates().copy()
    dim_products.to_sql('dim_products', engine, schema='olist', if_exists='replace', index=False)

    dim_sellers = df[['seller_id']].drop_duplicates().copy()
    dim_sellers.to_sql('dim_sellers', engine, schema='olist', if_exists='replace', index=False)

    dim_dates = df[['order_year', 'order_month']].drop_duplicates().copy()
    dim_dates.to_sql('dim_dates', engine, schema='olist', if_exists='replace', index=False)

    logger.info('Loaded curated data into PostgreSQL schema olist')


if __name__ == '__main__':
    load_to_postgres()
