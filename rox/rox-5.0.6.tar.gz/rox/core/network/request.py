import requests


class RequestData:
    def __init__(self, url, query_params):
        self.url = url
        self.query_params = query_params if query_params is not None else {}

class Request:
    def send_get(self, request_data):
        resp = requests.get(request_data.url, params=request_data.query_params, timeout=30)
        return resp

    def send_post(self, request_data):
        resp = requests.post(request_data.url, json=request_data.query_params, timeout=30)
        return resp
