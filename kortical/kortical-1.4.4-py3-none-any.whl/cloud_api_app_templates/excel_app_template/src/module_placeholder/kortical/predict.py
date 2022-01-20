import logging
import pandas as pd
import requests

from module_placeholder.config import read_config

logger = logging.getLogger(__name__)

config = read_config("predict.yml")
predict_url = config['predict_url']
api_key = config['api_key']


def check_and_parse_response(response):
    if response.headers['content-type'] == 'application/json':
        response_dict = response.json()
        if 'result' in response_dict and response_dict['result'] == 'error':
            raise Exception(f"{response.status_code} - {response_dict['message']}")
        else:
            return response_dict
    else:
        response.raise_for_status()


def run_kortical_prediction(df):
    df = df.reset_index()
    num_rows_per_batch = 2000
    df_out_batches = []
    number_of_batches = int(len(df) / num_rows_per_batch + 1)
    for i in range(number_of_batches):
        batch_size = min(num_rows_per_batch, len(df) - i*num_rows_per_batch)
        if batch_size > 0:
            start_index = i*num_rows_per_batch
            df_as_json = df[start_index:start_index+batch_size].to_json(orient='split')
            response = requests.post(f"{predict_url}?flatten=true&explain_predictions=false&api_key={api_key}",
                                     data=df_as_json,
                                     headers={'Content-Type': 'application/json'})

            logger.info(f"Validating predict response for batch {i+1}/{number_of_batches}.")
            check_and_parse_response(response)

            response_df = pd.read_json(response.text, orient='split', convert_dates=False, dtype=False)
            df_out_batches.append(response_df)

    df_out = pd.concat(df_out_batches)
    return df_out