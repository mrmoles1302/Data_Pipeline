import logging
import math
import pickle
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

from config.settings import CURATED_DIR, LOG_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger(__name__)


def train_model() -> None:
    data = pd.read_parquet(CURATED_DIR / 'olist_curated.parquet')
    if 'delivery_days' not in data.columns:
        data['delivery_days'] = data.get('avg_delivery_days', pd.Series(0.0, index=data.index))
    data = data.dropna(subset=['delivery_days'])
    features = ['customer_state', 'product_category_name_english', 'seller_id', 'monthly_revenue', 'review_score_avg']
    target = 'delivery_days'
    X = data[features]
    y = data[target]

    numeric_features = ['monthly_revenue', 'review_score_avg']
    categorical_features = ['customer_state', 'product_category_name_english', 'seller_id']

    preprocessor = ColumnTransformer(transformers=[
        ('num', SimpleImputer(strategy='median'), numeric_features),
        ('cat', Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), categorical_features),
    ])

    model = Pipeline(steps=[('preprocess', preprocessor), ('model', RandomForestRegressor(n_estimators=20, random_state=42, n_jobs=-1))])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    rmse = math.sqrt(mse)
    r2 = r2_score(y_test, preds)

    output_dir = Path(__file__).resolve().parent / 'models'
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'model.pkl', 'wb') as fh:
        pickle.dump(model, fh)

    logger.info('MAE=%s RMSE=%s R2=%s', mae, rmse, r2)


if __name__ == '__main__':
    train_model()
