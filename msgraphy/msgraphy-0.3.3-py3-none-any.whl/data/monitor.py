import requests

from msgraphy.data import graphdataclass


@graphdataclass
class AsyncJobStatus:
    percentage_complete: float
    resource_id: str
    status: str


class Monitor:

    def __init__(self, response: requests.Response):
        self.__response = response

    @staticmethod
    def from_response(response: requests.Response):
        return Monitor(response)

    @property
    def location(self):
        return self.__response.headers['Location']

    def __str__(self):
        return f"Monitor[{self.location}]"
