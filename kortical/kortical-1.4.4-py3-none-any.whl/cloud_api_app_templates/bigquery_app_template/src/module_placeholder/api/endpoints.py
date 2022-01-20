from flask import Response
import logging
from tempfile import NamedTemporaryFile

from module_placeholder.authentication import safe_api_call
from module_placeholder.bigquery.bigquery import create_dataframe_from_bigquery, insert_dataframe_into_bigquery
from module_placeholder.kortical.predict import run_kortical_prediction

logger = logging.getLogger(__name__)


def register_routes(app):
    @app.route('/update_bigquery', methods=['get'])
    @safe_api_call
    def update_bigquery():
        df = create_dataframe_from_bigquery()
        df = run_kortical_prediction(df)
        insert_dataframe_into_bigquery(df)
        return Response("Success!")