# coding: utf-8
import json

import requests


def send_post(j_data, target_url, method="POST"):
    if method == "POST":
        result = requests.post(target_url, data=json.dumps(j_data), headers={'Content-Type': 'application/json'})
    else:
        result = requests.get(target_url)
    return result.text
