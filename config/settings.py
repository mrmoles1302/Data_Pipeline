from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
CURATED_DIR = DATA_DIR / 'curated'
SOURCE_DATA_DIR = Path('/home/vignesh/projects/Data_Pipeline/datasets')

POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres')

RAW_FILES = {
    'customers': 'olist_customers_dataset.csv',
    'geolocation': 'olist_geolocation_dataset.csv',
    'order_items': 'olist_order_items_dataset.csv',
    'order_payments': 'olist_order_payments_dataset.csv',
    'order_reviews': 'olist_order_reviews_dataset.csv',
    'orders': 'olist_orders_dataset.csv',
    'products': 'olist_products_dataset.csv',
    'sellers': 'olist_sellers_dataset.csv',
    'category_translation': 'product_category_name_translation.csv',
}

LOG_FILE = BASE_DIR / 'monitoring' / 'logs' / 'pipeline.log'
