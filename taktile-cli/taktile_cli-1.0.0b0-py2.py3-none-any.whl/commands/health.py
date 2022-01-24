import requests
from pyarrow._flight import FlightCancelledError  # type: ignore
from pyarrow.flight import FlightClient  # type: ignore

from tktl.commands import BaseGrpcClientCommand, BaseRestClientCommand
from tktl.core.clients import API
from tktl.core.exceptions import APIClientException


class GetRestHealthCommand(BaseRestClientCommand):
    def execute(self):
        if self.client.local:
            self.client.set_client_and_location(
                location=self.client.local_endpoint,
                client=API(api_url=self.client.local_endpoint),
            )
        else:
            self.client._authenticate(health_check=True)
        try:
            response = self.client.health()
        except APIClientException as e:
            error_str = f"Service is not running properly: {repr(e.detail)}"
            self.client.logger.error(error_str)
            raise APIClientException(detail=error_str, status_code=e.status_code)
        except requests.exceptions.RequestException as e:
            error_str = f"Unable to decode server response: {repr(e)}"
            self.client.logger.error(error_str)
            raise APIClientException(detail=error_str, status_code=400)
        if response.status_code < 400:
            self.client.logger.log(
                f"Service at {self.client.location} is up and running", color="green"
            )
            return response


class GetGrpcHealthCommand(BaseGrpcClientCommand):
    def execute(self):
        if self.client.local:
            self.client.set_client_and_location(
                location=self.client.local_endpoint,
                client=FlightClient(location=self.client.local_endpoint),
            )
        else:
            try:
                self.client._authenticate(health_check=True)
            except FlightCancelledError as e:
                error_str = f"Service is not running properly: {repr(e)}"
                self.client.logger.error(error_str)
                raise APIClientException(detail=error_str, status_code=404)
        try:
            response = self.client.health()
        except APIClientException as e:
            error_str = f"Service is not running properly: {repr(e.detail)}"
            self.client.logger.error(error_str)

            raise APIClientException(detail=error_str, status_code=e.status_code)

        self.client.logger.log(
            f"Service at {self.client.location} is up and running", color="green"
        )
        return response
