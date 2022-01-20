
from abc import ABCMeta, abstractmethod


class AbstractHTTPClient(metaclass=ABCMeta):

    @abstractmethod
    def send(self, endpoint, method, json=None, files=None, headers=None, params=None, **kwargs):
        pass

    @abstractmethod
    def get(self, endpoint, headers=None, params=None, **kwargs):
        pass

    @abstractmethod
    def post(self, endpoint, json=None, files=None, headers=None, **kwargs):
        pass

    @abstractmethod
    def patch(self, endpoint, json=None, files=None, headers=None, **kwargs):
        pass

    @abstractmethod
    def put(self, endpoint, json=None, files=None, headers=None, **kwargs):
        pass

    @abstractmethod
    def delete(self, endpoint, headers=None, **kwargs):
        pass

