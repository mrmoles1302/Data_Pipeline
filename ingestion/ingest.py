import json
import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

from config.settings import BASE_DIR, RAW_DIR, SOURCE_DATA_DIR, RAW_FILES, LOG_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger(__name__)


def detect_files() -> List[Path]:
    return [SOURCE_DATA_DIR / name for name in RAW_FILES.values()]


def validate_schema(df: pd.DataFrame, expected_columns: List[str]) -> bool:
    return set(expected_columns).issubset(set(df.columns))


def collect_null_percentages(df: pd.DataFrame) -> Dict[str, float]:
    return {col: round(float(val), 4) for col, val in df.isna().mean().items()}


def ingest() -> Dict[str, object]:
    report: Dict[str, object] = {'files': []}
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for key, filename in RAW_FILES.items():
        src = SOURCE_DATA_DIR / filename
        dest = RAW_DIR / filename
        df = pd.read_csv(src)
        expected_columns = {
            'customers': ['customer_id', 'customer_unique_id', 'customer_zip_code_prefix', 'customer_city', 'customer_state'],
            'geolocation': ['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng', 'geolocation_city', 'geolocation_state'],
            'order_items': ['order_id', 'order_item_id', 'product_id', 'seller_id', 'shipping_limit_date', 'price', 'freight_value'],
            'order_payments': ['order_id', 'payment_sequential', 'payment_type', 'payment_installments', 'payment_value'],
            'order_reviews': ['review_id', 'order_id', 'review_score', 'review_comment_title', 'review_comment_message', 'review_creation_date', 'review_answer_timestamp'],
            'orders': ['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'],
            'products': ['product_id', 'product_category_name', 'product_name_lenght', 'product_description_lenght', 'product_photos_qty', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'],
            'sellers': ['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state'],
            'category_translation': ['product_category_name', 'product_category_name_english'],
        }[key]

        if not validate_schema(df, expected_columns):
            raise ValueError(f'Schema validation failed for {filename}')

        duplicates = int(df.duplicated().sum())
        nulls = collect_null_percentages(df)
        df.to_csv(dest, index=False)

        report['files'].append({
            'table': key,
            'source': str(src),
            'destination': str(dest),
            'rows': int(len(df)),
            'columns': int(len(df.columns)),
            'duplicates': duplicates,
            'null_percentages': nulls,
            'schema_valid': True,
        })
        logger.info('Ingested %s rows from %s', len(df), filename)

    report_path = BASE_DIR / 'ingestion_report.json'
    with open(report_path, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2)

    logger.info('Saved ingestion report to %s', report_path)
    return report


if __name__ == '__main__':
    ingest()
