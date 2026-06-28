import json
import logging
from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from config.settings import RAW_DIR, PROCESSED_DIR, CURATED_DIR, LOG_FILE, RAW_FILES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def build_spark_session() -> SparkSession:
    return SparkSession.builder.master('local[*]').appName('olist-etl').config('spark.sql.shuffle.partitions', '2').getOrCreate()


def load_raw_tables() -> dict:
    tables = {}
    for key, filename in RAW_FILES.items():
        path = RAW_DIR / filename
        tables[key] = pd.read_csv(path)
    return tables


def clean_and_transform(spark: SparkSession) -> None:
    tables = load_raw_tables()
    customers = tables['customers']
    orders = tables['orders']
    order_items = tables['order_items']
    payments = tables['order_payments']
    reviews = tables['order_reviews']
    products = tables['products']
    sellers = tables['sellers']
    category_translation = tables['category_translation']

    customers['customer_zip_code_prefix'] = pd.to_numeric(customers['customer_zip_code_prefix'], errors='coerce').fillna(0).astype(int)

    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'], errors='coerce')
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'], errors='coerce')
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'], errors='coerce')
    orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'], errors='coerce')
    orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'], errors='coerce')

    order_items['price'] = pd.to_numeric(order_items['price'], errors='coerce').fillna(0.0)
    order_items['freight_value'] = pd.to_numeric(order_items['freight_value'], errors='coerce').fillna(0.0)
    payments['payment_value'] = pd.to_numeric(payments['payment_value'], errors='coerce').fillna(0.0)
    reviews['review_score'] = pd.to_numeric(reviews['review_score'], errors='coerce').fillna(0.0)
    reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'], errors='coerce')
    reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'], errors='coerce')

    orders_enriched = (
        orders
        .merge(customers, on='customer_id', how='left')
        .merge(order_items, on='order_id', how='left')
        .merge(payments, on='order_id', how='left')
        .merge(reviews, on='order_id', how='left')
        .merge(products, on='product_id', how='left')
        .merge(sellers, on='seller_id', how='left')
        .merge(category_translation, on='product_category_name', how='left')
    )

    orders_enriched['total_order_value'] = orders_enriched['price'].fillna(0.0) + orders_enriched['freight_value'].fillna(0.0)
    orders_enriched['delivery_days'] = (
        (orders_enriched['order_delivered_customer_date'] - orders_enriched['order_purchase_timestamp'])
        .dt.total_seconds()
        .div(86400)
    )
    orders_enriched['delivery_days'] = orders_enriched['delivery_days'].fillna(0.0)
    orders_enriched['order_year'] = orders_enriched['order_purchase_timestamp'].dt.year.fillna(0).astype(int)
    orders_enriched['order_month'] = orders_enriched['order_purchase_timestamp'].dt.month.fillna(0).astype(int)

    grouped = orders_enriched.groupby(
        [
            'order_year',
            'order_month',
            'customer_id',
            'customer_unique_id',
            'customer_city',
            'customer_state',
            'seller_id',
            'product_id',
            'product_category_name_english',
        ],
        dropna=False,
        observed=False,
    )

    pdf = grouped.agg(
        monthly_revenue=('total_order_value', 'sum'),
        avg_delivery_days=('delivery_days', 'mean'),
        review_score_avg=('review_score', 'mean'),
    ).reset_index()

    pdf['customer_lifetime_value'] = pdf['monthly_revenue']
    pdf['review_score_avg'] = pdf['review_score_avg'].fillna(0.0)
    pdf['avg_delivery_days'] = pdf['avg_delivery_days'].fillna(0.0)
    pdf['monthly_revenue'] = pdf['monthly_revenue'].fillna(0.0)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CURATED_DIR.mkdir(parents=True, exist_ok=True)

    curated_path = CURATED_DIR / 'olist_curated.parquet'
    processed_path = PROCESSED_DIR / 'olist_curated.parquet'

    pdf.to_parquet(curated_path, index=False)

    spark_df = spark.createDataFrame(pdf)
    spark_df.write.mode('overwrite').partitionBy('order_year', 'order_month').parquet(str(processed_path))

    partition_values = spark_df.select('order_year', 'order_month').distinct().collect()
    catalog = {
        'partitions': [
            {
                'year': int(row['order_year']),
                'month': int(row['order_month']),
                'path': f"{processed_path}/year={int(row['order_year'])}/month={int(row['order_month'])}",
            }
            for row in sorted(partition_values, key=lambda r: (int(r['order_year']), int(r['order_month'])))
        ]
    }
    with open(PROCESSED_DIR.parent / 'data_catalog.json', 'w', encoding='utf-8') as fh:
        json.dump(catalog, fh, indent=2)

    logger.info('Spark processing complete')


def main() -> None:
    spark = build_spark_session()
    try:
        clean_and_transform(spark)
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
