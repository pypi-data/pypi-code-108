import os
import requests
from google.protobuf.json_format import MessageToDict


def launch_experiment(xp, organisation, dataset_slug, view_uuid, model_name, url_prefix=None, api_key=None):
    if url_prefix is None:
        url_prefix = os.getenv('DEEPOMATIC_STUDIO_API_PREFIX', 'https://studio.deepomatic.com/api')
    if api_key is None:
        api_key = os.getenv('DEEPOMATIC_API_KEY')
        if api_key is None:
            raise Exception("Could not find API key, please set environment variable 'DEEPOMATIC_API_KEY'.")

    def make_request(url_prefix, url, api_key, body=None):
        url = os.path.join(url_prefix, url)
        headers = {
            'X-API-KEY': api_key
        }
        if body is None:
            r = requests.get(url, headers=headers)
        else:
            r = requests.post(url, json=body, headers=headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception('Invalid status code {} for url {}, response: {}'.format(r.status_code, url, r.text))

    # Trigger the training
    url = 'orgs/{}/datasets/{}/views/{}/models/train/'.format(organisation, dataset_slug, view_uuid)
    body = {
        'model_name': model_name,
        'experiment': MessageToDict(xp),
    }
    return make_request(url_prefix, url, api_key, body)
