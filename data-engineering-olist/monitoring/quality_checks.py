import json
import logging
from pathlib import Path

import json
import pandas as pd
import great_expectations as gx
from great_expectations.core.batch import Batch
from great_expectations.execution_engine import PandasExecutionEngine
from great_expectations.validator.validator import Validator

from config.settings import CURATED_DIR, LOG_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger(__name__)


def run_quality_checks() -> None:
    data = pd.read_parquet(CURATED_DIR / 'olist_curated.parquet')
    context = gx.get_context()

    validator = Validator(
        execution_engine=PandasExecutionEngine(),
        expectation_suite=gx.ExpectationSuite('olist_curated_quality_checks'),
        data_context=context,
        batches=[Batch(data=data)],
    )

    validator.expect_column_values_to_not_be_null('monthly_revenue')
    validator.expect_column_values_to_be_between('review_score_avg', min_value=0, max_value=5)
    validator.expect_column_values_to_not_be_null('customer_id')

    results = validator.validate()
    logger.info('Great Expectations validation success=%s', results.success)
    if hasattr(results, 'to_json'):
        summary = results.to_json()
    elif hasattr(results, 'to_json_dict'):
        summary = json.dumps(results.to_json_dict(), default=str)
    elif hasattr(results, 'to_raw_dict'):
        summary = json.dumps(results.to_raw_dict(), default=str)
    elif hasattr(results, 'to_dict'):
        try:
            summary = json.dumps(results.to_dict(), default=str)
        except Exception:
            summary = str(results)
    else:
        summary = str(results)
    logger.info('Great Expectations validation summary: %s', summary)


if __name__ == '__main__':
    run_quality_checks()
