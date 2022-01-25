import requests


class ApiContext:

    @staticmethod
    def execute_get_request(url: str, params: dict = None):
        response = requests.get(url=url, params=params)
        return response

    @staticmethod
    def execute_put_request(url: str, data: dict = None):
        response = requests.put(url=url, data=data)
        return response

    @staticmethod
    def execute_post_request(url: str, data: dict):
        response = requests.post(url=url, data=data)
        return response
