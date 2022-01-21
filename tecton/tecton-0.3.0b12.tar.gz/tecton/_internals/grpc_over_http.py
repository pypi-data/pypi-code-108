import atexit
import base64
import os
import platform
import shutil
import tempfile
import threading
from concurrent import futures
from urllib.parse import urljoin

import grpc
import requests

import tecton

GRPC_OPTIONS = [
    ("grpc.max_message_length", 64 * 1024 * 1024),
    ("grpc.max_receive_message_length", 64 * 1024 * 1024),
    ("grpc.max_send_message_length", 64 * 1024 * 1024),
    ("grpc.enable_http_proxy", 0),
]


class _Executor(futures.ThreadPoolExecutor):
    def submit(self, *args, **kwargs):
        # This prevents errors from getting spammed to the console from "IngestClientLogs" RPCs that fire after
        # the main module exits
        try:
            super(_Executor, self).submit(*args, **kwargs)
        except RuntimeError as e:
            if len(e.args) >= 1 and e.args[0].startswith("cannot schedule new futures after"):
                error = futures.Future()
                error.set_exception(e)
                return error
            raise e


_channel = None
_server = None
_tempdir = None
_lock = threading.Lock()


def _cleanup():
    with _lock:
        if _tempdir:
            shutil.rmtree(_tempdir)


atexit.register(_cleanup)


def channel():
    """Returns a channel which will tunnel all gRPC requests via HTTP1.1 to the gRPC Gateway."""
    global _channel, _server, _tempdir, _lock
    with _lock:
        if not _channel:
            _tempdir = tempfile.mkdtemp()
            if platform.system() == "Windows":
                addr = f"localhost:54051"
            else:
                socket = os.path.join(_tempdir, "socket")
                addr = f"unix:{socket}"
            executor = _Executor(max_workers=5)
            _server = grpc.server(thread_pool=executor, handlers=[_ServiceHandler()], options=GRPC_OPTIONS)
            _server.add_insecure_port(addr)
            _server.start()
            _channel = grpc.insecure_channel(addr, GRPC_OPTIONS)
        return _channel


class _ServiceHandler(grpc.GenericRpcHandler):
    def service(self, handler_call_details):
        return _MethodHandler(handler_call_details.method, handler_call_details.invocation_metadata)


_CODE_TO_CODE_OBJECT = {x.value[0]: x for x in grpc.StatusCode}


# That creates requests session and the underlying connection pool
requests_session = requests.Session()


class _MethodHandler(grpc.RpcMethodHandler):
    request_streaming = False
    response_streaming = False
    request_deserializer = None
    response_serializer = None

    def __init__(self, method, metadata):
        self._method = method
        self._metadata = metadata

    def unary_unary(self, request, ctx):
        proxy_request = {
            "method": self._method,
            "metadata": {m.key: m.value for m in self._metadata},
            "request": base64.encodebytes(request).decode("utf-8"),
        }

        global requests_session
        response = requests_session.post(self._url(), json=proxy_request, timeout=300.0)
        response.raise_for_status()
        body = response.json()

        if "status" in body and body["status"]["code"] != 0:
            ctx.abort(_CODE_TO_CODE_OBJECT[body["status"]["code"]], body["status"]["detail"])
            return
        return base64.decodebytes(body["response"].encode("utf-8"))

    @staticmethod
    def _url():
        api_service = tecton.conf.get_or_none("API_SERVICE")
        assert api_service is not None, "API_SERVICE must be set in tecton.conf"
        if "localhost" not in api_service and "ingress" not in api_service:
            assert api_service.endswith("/api"), "API_SERVICE should look like https://<deployment-name>.tecton.ai/api"
        return urljoin(api_service + "/", "proxy")
