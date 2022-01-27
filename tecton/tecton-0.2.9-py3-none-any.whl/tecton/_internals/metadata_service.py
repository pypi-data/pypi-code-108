import collections
import logging

import grpc
import pendulum
from google.protobuf.empty_pb2 import Empty
from grpc import RpcError
from grpc import StatusCode

import tecton
from tecton import conf
from tecton import okta
from tecton._internals import errors
from tecton._internals import grpc_over_http
from tecton._internals.tecton_errors import FailedPreconditionError
from tecton._internals.tecton_errors import TectonAPIInaccessibleError
from tecton._internals.tecton_errors import TectonAPIValidationError
from tecton_proto.metadataservice import metadata_service_pb2
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.logger import get_logging_level

_stub_instance = None
_trace_id = None

logger = get_logger("metadata_service")


def instance():
    if not _stub_instance:
        _init_stub_instance()
    return _stub_instance


def close_instance():
    if _stub_instance:
        _stub_instance.close()


def is_initialized():
    return _stub_instance is not None


def set_trace_id(trace_id):
    global _trace_id
    _trace_id = trace_id


def _get_host_port():
    return conf.get_or_none("METADATA_SERVICE")


def _get_direct_channel():
    channel_options = [
        ("grpc.max_message_length", 64 * 1024 * 1024),
        ("grpc.max_receive_message_length", 64 * 1024 * 1024),
    ]
    return grpc.insecure_channel(_get_host_port(), options=channel_options)


def _init_stub_instance():
    global _stub_instance

    if conf.get_or_none("USE_DIRECT_GRPC"):
        channel = _get_direct_channel()
    else:
        channel = grpc_over_http.channel()
    intercept_channel = grpc.intercept_channel(channel, MetadataServiceInterceptor())
    _stub_instance = MetadataServiceStub(intercept_channel)
    conf._init_metadata_server_config(_stub_instance.GetConfigs(Empty()))


class MetadataServiceStub(object):
    # Due to https://github.com/stackb/rules_proto/issues/113 generating GRPC
    # classes using protoc is not working. This is manually recreating what
    # protoc does for the client side of GRPC services. It only supports unary-unary.
    # If anything else is needed hopefully that bug has been fixed.
    def __init__(self, channel):
        service_descriptor = metadata_service_pb2.DESCRIPTOR.services_by_name["MetadataService"]
        for method in service_descriptor.methods:
            if method.input_type.name == "Empty":
                request_serializer = Empty.SerializeToString
            else:
                request_serializer = getattr(metadata_service_pb2, method.input_type.name).SerializeToString
            if method.output_type.name == "Empty":
                response_deserializer = Empty.FromString
            else:
                response_deserializer = getattr(metadata_service_pb2, method.output_type.name).FromString
            fn = channel.unary_unary(
                f"/{service_descriptor.full_name}/{method.name}",
                request_serializer=request_serializer,
                response_deserializer=response_deserializer,
            )
            self._channel = channel
            setattr(self, method.name, fn)

    def close(self):
        self._channel.close()


class _ClientCallDetails(
    collections.namedtuple("_ClientCallDetails", ("method", "timeout", "metadata", "credentials")),
    grpc.ClientCallDetails,
):
    pass


class MetadataServiceInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.StreamUnaryClientInterceptor):
    """
    Adding headers based on an a example in
    https://github.com/grpc/grpc/blob/master/examples/python/interceptors/headers/header_manipulator_client_interceptor.py
    """

    def __init__(self):
        pass

    @staticmethod
    def _intercept_call(continuation, client_call_details, request_or_iterator):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append(("x-request-id", IdHelper.generate_string_id()))
        if _trace_id:
            metadata.append(("x-trace-id", _trace_id))

        version = tecton.version.get_version()
        # when running from dev environment, package version might not be set
        if version:
            metadata.append(("x-tecton-client-version", version))

        workspace = conf.get_or_none("TECTON_WORKSPACE")
        if workspace:
            metadata.append(("x-workspace", workspace))
            if workspace.endswith("__emr"):
                metadata.append(("x-tecton-force-emr", "true"))

        client_call_details = _ClientCallDetails(
            client_call_details.method, client_call_details.timeout, metadata, client_call_details.credentials
        )

        token = okta.get_token_refresh_if_needed()
        authorization = f"Bearer {token}"
        if not token:
            token = conf.get_or_none("TECTON_API_KEY")
            authorization = f"Tecton-key {token}"

        if token:
            metadata.append(("authorization", authorization))

        start_time = pendulum.now("UTC")

        response = continuation(client_call_details, request_or_iterator)

        e = response.exception()
        if not e:
            return response

        if isinstance(e, RpcError):
            if e.code() == StatusCode.UNAVAILABLE:
                raise TectonAPIInaccessibleError(e.details(), _get_host_port())

            if e.code() == StatusCode.INVALID_ARGUMENT:
                raise TectonAPIValidationError(e.details())

            if e.code() == StatusCode.FAILED_PRECONDITION:
                raise FailedPreconditionError(e.details())

            if e.code() == StatusCode.PERMISSION_DENIED:
                if not token:
                    raise PermissionError(
                        "Tecton credentials are not configured or have expired. Run `tecton login` to authenticate."
                    )
                else:
                    raise PermissionError(f"Configured Tecton credentials are not valid ({e.details()})")

        if get_logging_level() < logging.INFO:
            raise e

        raise errors.INTERNAL_ERROR_FROM_MDS(e.details(), _trace_id)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return self._intercept_call(continuation, client_call_details, request_iterator)
