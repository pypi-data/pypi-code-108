from flask import Response
import logging
from tempfile import NamedTemporaryFile

from module_placeholder.authentication import safe_api_call
from module_placeholder.bigquery.bigquery import create_dataframe_from_bigquery
from module_placeholder.kortical.predict import run_kortical_prediction
from module_placeholder.excel import create_workbook_from_template

logger = logging.getLogger(__name__)


def register_routes(app):
    @app.route('/latest_churn.xlsx', methods=['get'])
    @safe_api_call
    def get_churn_spreadsheet():
        logger.info('Creating churn spreadsheet.')
        df = create_dataframe_from_bigquery()
        df = run_kortical_prediction(df)
        logger.info("Writing to excel spreadsheet")
        with NamedTemporaryFile() as tempfile:
            create_workbook_from_template(tempfile, "churn_template.xlsx", df)
            logger.debug('Returning excel spreadsheet')
            return Response(tempfile.read(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
