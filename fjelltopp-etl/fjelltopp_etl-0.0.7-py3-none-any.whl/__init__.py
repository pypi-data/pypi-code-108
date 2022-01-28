import pandas as pd

import etl.logging as logging
LOGGER = logging.get_logger()

import etl.decorators as decorators
import etl.data_cleanup as data_cleanup
import etl.data_processing as data_processing
import etl.db_util as db_util
import etl.requests_util as requests_util
import etl.secrets as secrets
import etl.sources as sources


def null_step(df: pd.DataFrame) -> pd.DataFrame:
    return df


def add_empty_column(column_name):
    def _add_empty_column(df: pd.DataFrame) -> pd.DataFrame:
        df[column_name] = ''
        return df

    return _add_empty_column
