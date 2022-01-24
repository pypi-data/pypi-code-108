import os
import time
import logging
import requests
import traceback

import pandas_gbq as gbq
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv, find_dotenv

from trell_ai_util.constants import *

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
credentials = Credentials.from_service_account_file(BIG_QUERY_SERVICE_ACCOUNT_CRED)


bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)


def insert_rows_array_in_bigquery(dataset=None, table=None, rows_to_insert=None):
    try:

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = BIG_QUERY_SERVICE_ACCOUNT_CRED
        bq_client = bigquery.Client()
        table = '{0}.{1}.{2}'.format(WRITE_BIG_QUERY_PROJECT, dataset, table)
        rows_to_insert = rows_to_insert
        errors = bq_client.insert_rows_json(table, rows_to_insert)
        assert errors == []
    except Exception as err:
        logging.error(err)
        logging.info(traceback.format_exc())


def insert_rows_in_bigquery(dataset=None, table=None, rows_to_insert=None):
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = BIG_QUERY_SERVICE_ACCOUNT_CRED
        bq_client = bigquery.Client()
        table_id = '{0}.{1}.{2}'.format(WRITE_BIG_QUERY_PROJECT, dataset, table)
        table = bq_client.get_table(table_id)
        errors = bq_client.insert_rows(table, rows_to_insert)
        if not errors:
            print("Rows added successfully")
        else:
            print("Failed adding rows", '\n', errors)
    except Exception as err:
        logging.error(err)
        logging.info(traceback.format_exc())


def get_bigquery_data_from_query(query=None, query_config=None, max_retries=0, time_interval=5):

    flag = True
    while (flag):
        try:
            if query:
                df = gbq.read_gbq(query=query, project_id=READ_BIG_QUERY_PROJECT,
                                  configuration=query_config, credentials=credentials)
                return df
            else:
                return "Query is None"
            flag = False
        except requests.exceptions.Timeout:
            logging.info("readtimeot - - - - - - - - waiting for {} seconds".format(time_interval))
            max_retries = max_retries - 1
            flag = False if max_retries <= 0 else True
            time.sleep(time_interval)
        except Exception as err:
            logging.error(err)
            logging.info(traceback.format_exc())
            flag = False


def dump_dataframe_to_bigquery_table(dataset=None, table=None, dataframe=None, mode="append"):
    try:
        gbq.to_gbq(dataframe, '{}.{}'.format(dataset, table), WRITE_BIG_QUERY_PROJECT, if_exists=mode,
                   credentials=credentials)
        print("Appending Done")
    except Exception as err:
        logging.error(err)
        logging.info(traceback.format_exc())


def execute_bigquery_query(query, query_config=None, timeout=900, max_retries=0, time_interval=5):
    flag = True
    while flag:
        try:
            query_job = bq_client.query(query, job_config=query_config)  # API request
            query_job.result(timeout=timeout)  # Waits for statement to finish
            logging.info("Executed auery -- ", query)
            flag = False
        except requests.exceptions.Timeout:
            logging.info("readtimeot - - - - - - - - waiting for {} seconds".format(time_interval))
            max_retries = max_retries - 1
            flag = False if max_retries <= 0 else True
            time.sleep(time_interval)
        except Exception as err:
            logging.error(err)
            logging.info(traceback.format_exc())
            flag = False
