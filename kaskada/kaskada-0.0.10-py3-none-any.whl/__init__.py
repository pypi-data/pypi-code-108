"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from kaskada.client import Client
import kaskada.formatters

import grpc
import IPython
import os
import sys
import traceback

import kaskada.errdetails.v1alpha.fenl_diagnostics_pb2 as kaskada_error_details_pb2

from grpc_status import rpc_status
from google.rpc import error_details_pb2

# Module global client configured at initialization time. By default, all API calls utilize the global client config
KASKADA_DEFAULT_CLIENT = None
# Client ID environment variable to authenticate with the API
KASKADA_CLIENT_ID_ENV = 'KASKADA_CLIENT_ID'
# Client Secret environment variable to authenticate with the API
KASKADA_CLIENT_SECRET_ENV = 'KASKADA_CLIENT_SECRET'
# Public API endpoint for Kaskada service
KASKADA_API_ENDPOINT = 'api.kaskada.com:50051'
# Authentication endpoint for Kaskada service. JWTs exchange authentication endpoint.
KASKADA_AUTH_ENDPOINT = 'prod-kaskada.us.auth0.com'
# Authentication audience for JWTs creation.
KASKADA_AUTH_AUDIENCE = 'https://api.prod.kaskada.com'
# Demo Kaskada Client ID has read-only permissions
KASKADA_DEMO_CLIENT_ID = 'lWYFx0020u4oulh7Z9UB8C5YXVRHNyk4'

def showtraceback(self, running_compiled_code=True):
    traceback_lines = traceback.format_exception(*sys.exc_info())
    message = traceback_lines[-1]
    sys.stderr.write(message)

IPython.core.interactiveshell.InteractiveShell.showtraceback = showtraceback

def init(client_id: str = None, client_secret: str = None, exchange_endpoint: str = None, audience: str = None, endpoint: str = None, is_secure: bool = True, demo: bool = False):
    """
    Initializes the Kaskada library with a client. Creating a client will update the default module default client.

    Args:
        client_id (str, optional): Kaskada Client ID.
        client_secret (str, optional): Kaskada Client Secret.
        exchange_endpoint (str, optional): Authentication endpoint to exchange JWTs.
        audience (str, optional): Authentication audience.
        endpoint (str, optional): API Endpoint.
        is_secure (bool, optional): Use SSL connection. Defaults to True.
        demo (bool, optional): Demo mode). Defaults to False.

    Returns:
        Client: Kaskada Client
    """
    if demo:
        demo_only(endpoint=endpoint, is_secure=is_secure)
    else:
        client(client_id=client_id, client_secret=client_secret, exchange_endpoint=exchange_endpoint, audience=audience, endpoint=endpoint, is_secure=is_secure)

    kaskada.formatters.try_init()

def demo_only(client_id: str = None, endpoint: str = None, is_secure: bool = True):
    """
    Initializes the Kaskada library with a demo only client.

    Args:
        client_id (str, optional): The demo only client ID. Defaults to KASKADA_DEMO_CLIENT_ID.
        endpoint (str, optional): API Endpoint. Defaults to KASKADA_API_ENDPOINT.
        is_secure (bool, optional): Use SSL connection. Defaults to True.

    Returns:
        Client: Kaskada Client
    """
    if client_id is None:
        client_id = KASKADA_DEMO_CLIENT_ID

    if endpoint is None:
        endpoint = KASKADA_API_ENDPOINT

    global KASKADA_DEFAULT_CLIENT
    KASKADA_DEFAULT_CLIENT = Client.demo_only(client_id, endpoint, is_secure)
    return KASKADA_DEFAULT_CLIENT

def client(client_id: str = None, client_secret: str = None, exchange_endpoint: str = None, audience: str = None, endpoint: str = None, is_secure: bool = True) -> Client:
    """
    Initializes a Kaskada Client. Used for overloading default production parameters. Creating a client will update the default module default client.

    Args:
        client_id (str, optional): Kaskada Client ID. Defaults to environment variable KASKADA_CLIENT_ID.
        client_secret (str, optional): Kaskada Client Secret. Defaults to environment variable KASKADA_CLIENT_SECRET.
        exchange_endpoint (str, optional): Authentication endpoint to exchange JWTs. Defaults to KASKADA_AUTH_ENDPOINT.
        audience (str, optional): Authentication audience. Defaults to KASKADA_AUTH_AUDIENCE.
        endpoint (str, optional): API Endpoint. Defaults to KASKADA_API_ENDPOINT.
        is_secure (bool, optional): Use SSL connection. Defaults to True.

    Raises:
        ValueError: Provided Client ID is None.
        ValueError: Provided Client Secret is None

    Returns:
        Client: Kaskada Client
    """
    if client_id is None:
        client_id = os.getenv(KASKADA_CLIENT_ID_ENV)
    if client_id is None:
        raise ValueError("Unable to read Kaskada Client ID. Please provide client_id key word argument or set env var KASKADA_CLIENT_ID.")

    if client_secret is None:
        client_secret = os.getenv(KASKADA_CLIENT_SECRET_ENV)
    if client_secret is None:
        raise ValueError("Unable to read Kaskada Client Secret. Please provide client_secret key word argument or set env var KASKADA_CLIENT_SECRET.")

    if exchange_endpoint is None:
        exchange_endpoint = KASKADA_AUTH_ENDPOINT

    if audience is None:
        audience = KASKADA_AUTH_AUDIENCE

    if endpoint is None:
        endpoint = KASKADA_API_ENDPOINT

    global KASKADA_DEFAULT_CLIENT
    KASKADA_DEFAULT_CLIENT = Client.authorized(client_id, client_secret, exchange_endpoint, audience, endpoint, is_secure)
    return KASKADA_DEFAULT_CLIENT


def handleGrpcError(rpc_error: grpc.Call):
    """
    All methods calling `handleGrpcError` do so after detecting a RpcError.  Currently
    all our grpc calls perform a `UnaryUnaryMultiCallable` method, docs linked here:
    https://grpc.github.io/grpc/python/_modules/grpc.html#UnaryUnaryMultiCallable

    Calling a `UnaryUnaryMultiCallable` method results in one of the following:
        Returns:
            The response value for the RPC.

        Raises:
            RpcError: Indicating that the RPC terminated with non-OK status. The
            raised RpcError will also be a grpc.Call for the RPC affording the RPC's
            metadata, status code, and details.

    Methods on a `grpc.Call` object include the following.  Full docs here:
    https://grpc.github.io/grpc/python/_modules/grpc.html#Call

        code(): The StatusCode value for the RPC.
        details(): The details string of the RPC.

    The `grpc_status.rpc_status.from_call(call)` method helps extract details
    objects from `grpc.Call` objects. Docs here:
    https://grpc.github.io/grpc/python/_modules/grpc_status/rpc_status.html#from_call

        Args:
            call: A grpc.Call instance.

        Returns:
            A google.rpc.status.Status message representing the status of the RPC.

        Raises:
            ValueError: If the gRPC call's code or details are inconsistent with the
            status code and message inside of the google.rpc.status.Status.
    """
    errorMessage = "An error occurred in your request.\n\tError Code: {}\n".format(rpc_error.code().name)
    try:
        status = rpc_status.from_call(rpc_error)
        if status:
            unpacked = []
            errorMessage += "\tError Message: {}\n".format(status.message)
            for detail in status.details:
                try:
                    val = unpack_details(detail)
                    unpacked.append(val)
                except Exception:
                    # maybe report back to wren in the future
                    pass
            if len(unpacked) > 0:
                errorMessage += "Details: \n"
                for val in unpacked:
                    errorMessage += "\t{}\n".format(val)
            raise Exception(errorMessage) from None
    except ValueError:
        # maybe report back to wren in the future
        pass
    errorMessage += "\tError Message: {}\n".format(rpc_error.details())
    raise Exception(errorMessage) from None

def unpack_details(grpc_detail):
    """Unpack a grpc status detail field (which is a 'google.protobuf.Any' type).
    `Unpack()` checks the descriptor of the passed-in message object against the stored one
    and returns False if they don't match and does not attempt any unpacking; True otherwise.
        Source:
            https://github.com/protocolbuffers/protobuf/blob/master/python/google/protobuf/internal/well_known_types.py#L81
            https://github.com/protocolbuffers/protobuf/blob/master/python/google/protobuf/internal/python_message.py#L1135

        Raises:
            google.protobuf.message.DecodeError: If it can't deserialize the message object

    `Is()` checks if the `Any` message represents the given protocol buffer type.
    """
    if grpc_detail.Is(error_details_pb2.BadRequest.DESCRIPTOR):
        val = error_details_pb2.BadRequest()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(error_details_pb2.PreconditionFailure.DESCRIPTOR):
        val = error_details_pb2.PreconditionFailure()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(error_details_pb2.RetryInfo.DESCRIPTOR):
        val = error_details_pb2.RetryInfo()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(error_details_pb2.DebugInfo.DESCRIPTOR):
        val = error_details_pb2.DebugInfo()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(error_details_pb2.QuotaFailure.DESCRIPTOR):
        val = error_details_pb2.QuotaFailure()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(error_details_pb2.RequestInfo.DESCRIPTOR):
        val = error_details_pb2.RequestInfo()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(error_details_pb2.ResourceInfo.DESCRIPTOR):
        val = error_details_pb2.ResourceInfo()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(error_details_pb2.Help.DESCRIPTOR):
        val = error_details_pb2.Help()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(error_details_pb2.LocalizedMessage.DESCRIPTOR):
        val = error_details_pb2.LocalizedMessage()
        grpc_detail.Unpack(val)
        return val
    elif grpc_detail.Is(kaskada_error_details_pb2.FenlDiagnostics.DESCRIPTOR):
        val = kaskada_error_details_pb2.FenlDiagnostics()
        grpc_detail.Unpack(val)
        error_msgs = []
        for fenl_diagnostic in val.fenl_diagnostics:
            error_msgs.append(fenl_diagnostic.formatted.replace("\n", "\n\t"))
        return "\n".join(error_msgs)
    else:
        raise ValueError(grpc_detail.type_url)

def handleException(e: Exception):
    raise Exception("An exception occurred: {}".format(e)) from None

def validate_client(client: Client):
    if client == None:
        raise ValueError('Client must be provided')
    if client.computeStub == None:
        raise ValueError('Invalid client provided. Compute service stub was not initialized properly.')
    if client.viewStub == None:
        raise ValueError('Invalid client provided. View service stub was not initialized properly.')
    if client.tableStub == None:
        raise ValueError('Invalid client provided. Table service stubs was not initialized properly.')