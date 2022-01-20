import logging

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