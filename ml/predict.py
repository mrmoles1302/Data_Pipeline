import pickle
from pathlib import Path

import pandas as pd

from config.settings import CURATED_DIR


def predict() -> None:
    model_path = Path(__file__).resolve().parent / 'models' / 'model.pkl'
    with open(model_path, 'rb') as fh:
        model = pickle.load(fh)

    data = pd.read_parquet(CURATED_DIR / 'olist_curated.parquet')
    sample = data[['customer_state', 'product_category_name_english', 'seller_id', 'monthly_revenue', 'review_score_avg']].head(5)
    predictions = model.predict(sample)
    print(predictions)


if __name__ == '__main__':
    predict()
