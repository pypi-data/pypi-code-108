import requests

from tktl.commands import BaseGrpcClientCommand, BaseRestClientCommand
from tktl.core.exceptions import APIClientException


class GetRestHealthCommand(BaseRestClientCommand):
    def execute(self):
        try:
            self._get_client()
        except requests.exceptions.RequestException as e:
            error_str = f"Unable to decode server response: {repr(e)}"
            raise APIClientException(detail=error_str, status_code=400)


class GetGrpcHealthCommand(BaseGrpcClientCommand):
    def execute(self):
        self._get_client()
