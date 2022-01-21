import urllib.parse

import requests

from . import access

API_URI = "https://api.agilicus.com"


def query_audit(limit=None, token_id=None):
    access_token = access.get_access_token()
    headers = {}
    headers["Authorization"] = "Bearer {}".format(access_token.get())
    params = {}
    if limit:
        params["limit"] = limit

    if token_id:
        params["tokenid"] = token_id

    query = urllib.parse.urlencode(params)
    uri = "/gateway/audit?{}".format(query)
    response = requests.get(API_URI + uri, headers=headers)
    return response.text
