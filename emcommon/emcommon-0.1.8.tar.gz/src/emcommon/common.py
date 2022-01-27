"""
Common functions to be used elsewhere
"""

import requests


def process_http_code(response):
    """
    Process the HTTP code of the response
    """
    if not response.ok:
        print(response.reason)
        return False
    return response


def esi_request(url, req_type, body=None):
    """
    Make an ESI request
    """
    headers = {
        'User-Agent': 'eve-market.net/1.0',
    }
    if req_type == "GET":
        response = requests.get(url, headers=headers)
    elif req_type == "POST":
        response = requests.post(url, headers=headers, json=body)
    if process_http_code(response):
        return response.text
    return False
    