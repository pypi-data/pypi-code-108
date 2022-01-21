from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional, Tuple, cast
import uuid

from google.protobuf.timestamp_pb2 import Timestamp
import grpc
import jsonpickle

from jetpack import __version__
from jetpack._remote import codec
from jetpack._runtime.local import LocalStub
from jetpack.config import instrumentation, k8s, namespace
from jetpack.proto.runtime.v1alpha1 import remote_pb2, remote_pb2_grpc

# Instead of having individual clients per functionality (e.g. job), have a
# single client for our runtime.

# TODO(Landau): Move client functionality out of _job.client and centralize it
# here.

# TODO(landau): make this a param
MAX_MESSAGE_LENGTH: Final[int] = 10485760  # 10MB

# Prevent circular dependency
if TYPE_CHECKING:
    from jetpack._task.task import Task


class JetpackException(Exception):
    """Base class for exceptions in this module"""

    pass


class RuntimeException(JetpackException):
    """Exception raised for errors in the Jetpack runtime and kubernetes."""

    def __init__(self, message: str) -> None:
        self.message = message


class ApplicationException(JetpackException):
    """Exception raised for errors from application-code that is using the SDK.

    TODO DEV-157
    For exceptions raised by remote functions and jobs, we serialize the
    userland exception in the backend and save it here. The userland exception
    is re-raised by the SDK for the caller of the remote function or job.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class NoControllerAddressError(JetpackException):
    pass


class Client:
    def __init__(self) -> None:
        host = os.environ.get(
            "JETPACK_RUNTIME_SERVICE_HOST",
            "remotesvc.jetpack-runtime.svc.cluster.local",
        )
        port = os.environ.get("JETPACK_RUNTIME_SERVICE_PORT", "80")
        self.address: str = f"{host.strip()}:{port.strip()}"
        self.stub: Optional[remote_pb2_grpc.RemoteExecutorStub] = None

    def dial(self) -> remote_pb2_grpc.RemoteExecutorStub:
        if self.stub is None:
            if k8s.is_in_cluster():
                channel = grpc.aio.insecure_channel(
                    self.address,
                    options=[
                        ("grpc.max_send_message_length", MAX_MESSAGE_LENGTH),
                    ],
                )
                self.stub = remote_pb2_grpc.RemoteExecutorStub(channel)
            else:
                self.stub = LocalStub(client)
        return self.stub

    async def set_cron_jobs(
        self,
        cron_jobs: List[remote_pb2.CronJob],
    ) -> remote_pb2.SetCronJobsResponse:
        request = remote_pb2.SetCronJobsRequest(
            namespace=cast(str, namespace.get()),
            hostname=os.environ["HOSTNAME"],
            cron_jobs=cron_jobs,
        )
        stub = self.dial()
        response: remote_pb2.SetCronJobsResponse = await stub.SetCronJobs(request)
        return response

    async def create_task(
        self,
        task: Task,
        args: Optional[Tuple[Any, ...]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Creates a Jetpack task. How the task gets executed is up to
        jetpack runtime.

        Keyword arguments:
        task -- task to create
        """

        request = self._build_create_task_request(task, args, kwargs)
        response: remote_pb2.CreateTaskResponse = await self.dial().CreateTask(request)
        task.id = uuid.UUID(response.task_id)
        if task.is_scheduled:
            instrumentation.get_tracer().scheduled_task_created(task)
        else:
            instrumentation.get_tracer().task_created(task)

    async def post_result(
        self, exec_id: str, value: Any = None, error: Optional[Exception] = None
    ) -> remote_pb2.PostResultResponse:

        if not exec_id:
            # Note: value=None and error=None is acceptable because a job
            # can run successfully and return nothing.
            raise Exception("An exec_id is required to post a result")

        result = remote_pb2.Result()
        if error:
            result.error.code = remote_pb2.APPLICATION
            result.error.message = str(error)
            result.error.encoded_error = bytes(jsonpickle.encode(error), "utf-8")
        else:  # order matters, as 'value' can be None
            result.value.encoded_value = bytes(jsonpickle.encode(value), "utf-8")

        request = remote_pb2.PostResultRequest(
            exec_id=exec_id,
            result=result,
        )

        response = await self.dial().PostResult(request)
        return cast(remote_pb2.PostResultResponse, response)

    async def wait_for_result(self, task_id: uuid.UUID) -> Any:
        request = remote_pb2.WaitForResultRequest(task_id=str(task_id))
        response = await self.dial().WaitForResult(request)
        instrumentation.get_tracer().result_returned(task_id, response.result)
        return self._transform_response_exception(response)

    @staticmethod
    def _build_create_task_request(
        task: Task,
        args: Optional[Tuple[Any, ...]],
        kwargs: Optional[Dict[str, Any]],
    ) -> remote_pb2.CreateTaskRequest:
        encoded_args = b""
        if args or kwargs:
            encoded_args = codec.encode_args(
                args if args else None,
                kwargs if kwargs else None,
            ).encode("utf-8")

        current_namespace = namespace.get()
        task_proto_obj = remote_pb2.Task(
            qualified_symbol=task.jetpack_function.name(),
            encoded_args=encoded_args,
            hostname=os.environ.get("HOSTNAME", ""),  # k8s sets this
            target_time=Timestamp(seconds=task.target_time),
        )
        if current_namespace:
            task_proto_obj.namespace = current_namespace

        return remote_pb2.CreateTaskRequest(
            task=task_proto_obj, sdk_version=__version__
        )

    @staticmethod
    def _transform_response_exception(
        response: remote_pb2.WaitForResultResponse,
    ) -> Any:
        if response.result.HasField("error") and response.result.error.encoded_error:
            e = jsonpickle.decode(response.result.error.encoded_error)
            raise e
        elif response.result.HasField("value"):
            val = jsonpickle.decode(response.result.value.encoded_value)
            return val
        else:
            raise RuntimeException(
                f"Either 'value' or 'error' should be specified in response. Got: {response}"
            )


client = Client()
