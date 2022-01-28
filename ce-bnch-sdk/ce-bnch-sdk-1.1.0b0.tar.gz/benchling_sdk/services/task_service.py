from time import sleep, time

from benchling_api_client.api.tasks import get_task

from benchling_sdk.errors import WaitForTaskExpiredError
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.models import AsyncTask, AsyncTaskStatus
from benchling_sdk.services.base_service import BaseService


class TaskService(BaseService):
    """
    Tasks.

    Endpoints that perform expensive computations launch long-running tasks. These endpoints return the task ID (a
    UUID) in the response body.

    After launching a task, periodically invoke the Get a task endpoint with the task UUID (e.g., every 10
    seconds), until the status is no longer RUNNING.

    You can access a task for up to 30 minutes after its completion, after which its data will no longer be
    available.

    See https://benchling.com/api/reference#/Tasks
    """

    @api_method
    def get_by_id(self, task_id: str) -> AsyncTask:
        """
        Get a Task by ID.

        See https://benchling.com/api/reference#/Tasks/getTask
        """
        response = get_task.sync_detailed(client=self.client, task_id=task_id)
        return model_from_detailed(response)

    @api_method
    def wait_for_task(
        self, task_id: str, interval_wait_seconds: int = 1, max_wait_seconds: int = 30
    ) -> AsyncTask:
        """
        Wait for a task until completion or timeout.

        A blocking method which polls the Benchling API and will return an AsyncTask as
        soon as its status is not RUNNING (in progress). This does not guarantee that the
        task was successful, only that Benchling has finished executing it.

        If max_wait_seconds is exceeded, will raise
        :py:class:`benchling_sdk.errors.WaitForTaskExpiredError`

        :param task_id: The ID of the task to poll
        :param interval_wait_seconds: time to wait between API calls in seconds
        :param max_wait_seconds: maximum wait time in seconds before raising WaitForTaskExpiredError
        :return: The completed AsyncTask. Check `status` for success or failure
        :rtype: AsyncTask
        """
        start_time = time()
        response = self.get_by_id(task_id)
        while response.status == AsyncTaskStatus.RUNNING and time() - start_time <= max_wait_seconds:
            sleep(interval_wait_seconds)
            response = self.get_by_id(task_id)
        if response.status != AsyncTaskStatus.RUNNING:
            return response
        raise WaitForTaskExpiredError(
            message=f"Timed out waiting for task ID {task_id} " f"after {max_wait_seconds} seconds",
            task=response,
        )
