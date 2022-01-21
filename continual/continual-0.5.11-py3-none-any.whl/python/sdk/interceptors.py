import grpc
import collections
from typing import Callable


class ClientCallDetails(
    collections.namedtuple(
        "ClientCallDetails", ("method", "timeout", "metadata", "credentials")
    ),
    grpc.ClientCallDetails,
):
    """Concrete client call details object.

    grpc.ClientCallDetails is an abstract base class.
    """


class AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    """Adds API key to GRPC requests."""

    api_key_getter: Callable[[], str]

    def __init__(self, api_key_getter: Callable[[], str]):
        """Initialize authentication interceptor.

        This class takes a getter callable in order to support
        lazy loading of the api_key.

        Arguments:
            api_key_getter: Function that returns an api key.
        """
        self.api_key_getter = api_key_getter

    def intercept_unary_unary(self, continuation, client_call_details, request):
        api_key = self.api_key_getter()
        if api_key is not None and api_key != "":
            metadata = [("authorization", "Bearer " + api_key)]
        else:
            metadata = []
        client_call_details = ClientCallDetails(
            method=client_call_details.method,
            metadata=metadata,
            timeout=client_call_details.timeout,
            credentials=client_call_details.credentials,
        )
        return continuation(client_call_details, request)
