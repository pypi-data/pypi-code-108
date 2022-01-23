from typing import Any, Callable, Dict, Tuple

import grpc

from jetpack._remote import codec
from jetpack.proto.runtime.v1alpha1 import remote_pb2, remote_pb2_grpc


class Client:
    def __init__(self) -> None:
        self.address: str = "localhost:50051"
        self.channel: grpc.Channel
        self.stub: remote_pb2_grpc.RemoteExecutorStub
        self.is_dialed = False  # TODO: Mutex needed?

    def Dial(self) -> None:
        self.channel = grpc.insecure_channel(self.address)
        self.stub = remote_pb2_grpc.RemoteExecutorStub(self.channel)
        self.is_dialed = True

    def RemoteCall(
        self, request: remote_pb2.RemoteCallRequest
    ) -> remote_pb2.RemoteCallResponse:
        # Lazily connect to the network. Putting this here so we get a clean
        # API from the get-go, but in practice we might want to do the network
        # connection when a function is *imported* as a stub, rather than on the
        # actual function call (to reduce latency on the call)
        if not self.is_dialed:
            self.Dial()
        response: remote_pb2.RemoteCallResponse = self.stub.RemoteCall(request)
        return response

    def remote_function(self, symbol: str) -> Callable[..., Any]:
        def rpc_wrapper(*args: Any, **kwargs: Any) -> Any:
            request = call_as_proto(symbol, args, kwargs)
            response = self.RemoteCall(request)
            return codec.decode_result(response)

        return rpc_wrapper


def call_as_proto(
    symbol: str, args: Tuple[Any, ...], kwargs: Dict[str, Any]
) -> remote_pb2.RemoteCallRequest:
    request = remote_pb2.RemoteCallRequest()
    request.qualified_symbol = symbol
    request.json_args = codec.encode_args(args, kwargs)
    return request
