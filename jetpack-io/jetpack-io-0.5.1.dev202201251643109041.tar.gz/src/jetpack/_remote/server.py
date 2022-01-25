from concurrent import futures
from typing import Any, Callable, Dict

import grpc

from jetpack._remote import codec
from jetpack.proto.runtime.v1alpha1 import remote_pb2, remote_pb2_grpc


class Servicer(remote_pb2_grpc.RemoteExecutorServicer):
    def __init__(self) -> None:
        # TODO: Figure out if we need any locking around the symbol table.
        self.symbol_table: Dict[str, Callable[..., Any]] = {}  # TODO: lock?

    def export(self, fn: Callable[..., Any]) -> str:
        symbol = fn.__name__
        self.symbol_table[symbol] = fn
        return symbol

    def RemoteCall(
        self, request: remote_pb2.RemoteCallRequest, context: grpc.ServicerContext
    ) -> remote_pb2.RemoteCallResponse:
        fn = self.symbol_table[request.qualified_symbol]
        args, kwargs = codec.decode_args(request.json_args)
        result = fn(*args, **kwargs)
        return codec.encode_result(result)

    # Below are dummy implementation of LaunchJob(), LaunchBlockingJob(), and
    # PostResult() that throw NotImplemented exceptions.
    # These are required so that we fulfill the remote service interface.
    # In practice though, we should either unify the remote service
    # implementation in the SDK into a single class (this one) OR
    # separate the interface the SDK uses vs the interface the runtime uses.

    def CreateTask(
        self, request: remote_pb2.CreateTaskRequest, context: grpc.ServicerContext
    ) -> remote_pb2.CreateTaskResponse:
        return super().CreateTask(request, context)

    def PostResult(
        self,
        request: remote_pb2.PostResultRequest,
        context: grpc.ServicerContext,
    ) -> remote_pb2.PostResultResponse:
        return super().PostResult(request, context)

    def SetCronJobs(
        self,
        request: remote_pb2.SetCronJobsRequest,
        context: grpc.ServicerContext,
    ) -> remote_pb2.SetCronJobsResponse:
        return super().SetCronJobs(request, context)

    def WaitForResult(
        self,
        request: remote_pb2.WaitForResultRequest,
        context: grpc.ServicerContext,
    ) -> remote_pb2.WaitForResultResponse:
        return super().WaitForResult(request, context)


class Server:
    def __init__(self) -> None:
        self.servicer = Servicer()
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        remote_pb2_grpc.add_RemoteExecutorServicer_to_server(self.servicer, self.server)
        self.is_listening = False  # TODO: Mutex needed?

    def Listen(self) -> None:
        self.server.add_insecure_port("[::]:50051")
        self.server.start()
        self.is_listening = True

    def export(self, fn: Callable[..., Any]) -> str:
        # Connect to the network lazily
        if not self.is_listening:
            self.Listen()
        return self.servicer.export(fn)
