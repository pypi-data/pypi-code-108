import json

import requests

from . import traffic

API_URI = "https://api.agilicus.com"


def get_gateway_generate(**kwargs):
    token = traffic.get_traffic_token(**kwargs)

    headers = {}
    headers["Accept"] = "text/plain"
    headers["Content-type"] = "application/json"

    data = {}
    data["token"] = token

    api = API_URI + "/deployment/local-gateway-k8s/generate"
    response = requests.post(api, headers=headers, data=json.dumps(data))
    return response.text
