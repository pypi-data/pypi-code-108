from __future__ import annotations

import base64
import time
from typing import TYPE_CHECKING, Dict
import uuid

from jetpack._task.jetpack_function_with_client import JetpackFunctionWithClient
from jetpack.config import symbols
from jetpack.config.symbols import Symbol
from jetpack.proto.runtime.v1alpha1 import remote_pb2, remote_pb2_grpc

if TYPE_CHECKING:
    from jetpack._runtime.client import Client


class LocalStub(remote_pb2_grpc.RemoteExecutorStub):
    task_results: Dict[str, remote_pb2.Result] = {}
    scheduled_tasks: Dict[str, remote_pb2.Task] = {}

    def __init__(self, client: Client) -> None:
        self.client = client

    async def CreateTask(
        self,
        request: remote_pb2.CreateTaskRequest,
    ) -> remote_pb2.CreateTaskResponse:
        task_id = str(uuid.uuid4())
        if request.task.target_time.seconds <= time.time():
            func = symbols.get_symbol_table()[Symbol(request.task.qualified_symbol)]
            await JetpackFunctionWithClient(self.client, func).exec(
                task_id,
                base64.b64encode(request.task.encoded_args),
            )
        else:
            self.scheduled_tasks[task_id] = request.task
        return remote_pb2.CreateTaskResponse(
            task_id=task_id,
        )

    async def PostResult(
        self,
        request: remote_pb2.PostResultRequest,
    ) -> remote_pb2.PostResultResponse:
        self.task_results[request.exec_id] = request.result
        return remote_pb2.PostResultResponse()

    async def WaitForResult(
        self,
        request: remote_pb2.WaitForResultRequest,
    ) -> remote_pb2.WaitForResultResponse:
        return remote_pb2.WaitForResultResponse(
            result=self.task_results[request.task_id],
        )

    async def SetCronJobs(
        self,
        request: remote_pb2.SetCronJobsRequest,
    ) -> remote_pb2.SetCronJobsResponse:
        """
        This is a no op. To fetch cronjobs you can use cron.get_jobs()
        In the future we may want to simulate the registration process
        """
        return remote_pb2.SetCronJobsResponse()
