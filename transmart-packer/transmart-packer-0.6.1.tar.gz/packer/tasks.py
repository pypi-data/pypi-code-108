import abc
import logging
import os

import json

from celery import Celery, Task
from celery.exceptions import SoftTimeLimitExceeded, Ignore

from packer.task_status import Status, TaskStatus
from packer import auth
from .config import redis_config, task_config, celery_config, transmart_config, http_config
from .redis_client import redis

import requests

logger = logging.getLogger(__name__)


app = Celery('tasks', broker=redis_config['url'])
app.conf.update(**celery_config)
app.autodiscover_tasks(['packer.jobs'], 'jobs')

os.makedirs(task_config['data_dir'], exist_ok=True)


class BaseDataTask(Task, metaclass=abc.ABCMeta):

    def on_success(self, retval, task_id, args, kwargs):
        """Success handler.

        Run by the worker if the task executes successfully.

        Arguments:
            retval (Any): The return value of the task.
            task_id (str): Unique id of the executed task.
            args (Tuple): Original arguments for the executed task.
            kwargs (Dict): Original keyword arguments for the executed task.

        Returns:
            None: The return value of this handler is ignored.
        """
        self.update_status(status=Status.SUCCESS, message='Task finished successfully.')

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry handler.

        This is run by the worker when the task is to be retried.

        Arguments:
            exc (Exception): The exception sent to :meth:`retry`.
            task_id (str): Unique id of the retried task.
            args (Tuple): Original arguments for the retried task.
            kwargs (Dict): Original keyword arguments for the retried task.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Error handler.

        This is run by the worker when the task fails.

        Arguments:
            exc (Exception): The exception raised by the task.
            task_id (str): Unique id of the failed task.
            args (Tuple): Original arguments for the task that failed.
            kwargs (Dict): Original keyword arguments for the task that failed.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """
        if type(exc) == SoftTimeLimitExceeded:
            self.update_status(
                status=Status.CANCELLED,
                message='Task cancelled during execution or task passed time limit.'
            )
        else:
            self.update_status(
                status=Status.FAILED,
                message=f'Task failed with {exc.__class__.__name__}: {exc}'
            )

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Handler called after the task returns.

        Arguments:
            status (str): Current task state.
            retval (Any): Task return value/exception.
            task_id (str): Unique id of the task.
            args (Tuple): Original arguments for the task.
            kwargs (Dict): Original keyword arguments for the task.
            einfo (~billiard.einfo.ExceptionInfo): Exception information.

        Returns:
            None: The return value of this handler is ignored.
        """

    def __call__(self, *args, **kwargs):
        self.update_status(status=Status.RUNNING, message=f'Starting task.')
        super().__call__(*args, **kwargs)

    def get_data_dir(self, create=True):
        path = os.path.join(task_config['data_dir'], self.task_id)
        if create:
            os.makedirs(path, exist_ok=True)
        return path

    def open_writer(self, filename):
        return open(os.path.join(self.get_data_dir(), filename), 'w')

    @property
    def task_id(self):
        return self.request.id

    @property
    def task_status(self):
        return TaskStatus(self.task_id)

    @property
    def channel(self):
        obj = self.task_status.get()
        return f'channel:{obj.get("user")}'

    def update_status(self, status, message):
        """
        Send status update message through websocket, update job status in Redis.

        :param status: status code.
        :param message: message for client.
        """
        self.task_status.update(status=status, message=message)
        logger.info(f'Status update for {self.task_id}: {message} ({status})')
        redis.publish(
            self.channel,
            json.dumps({
                'task_id': self.task_id,
                'status': status,
                'message': message
            })
        )

    def observations_json(self, constraint):
        """
        :param self: Required for bind to BaseDataTask
        :param constraint: transmart API constraint to request
        :return: response body (json) of the observation call of transmart API
        """
        user = self.task_status.get().get('user')
        token = auth.get_impersonated_token_for_user(user)
        handle = f'{transmart_config.get("host")}/v2/observations'
        self.update_status(Status.FETCHING, f'Getting data from observations from {handle!r}')
        r = requests.post(url=handle,
                          json={'type': 'clinical', 'constraint': constraint},
                          headers={
                              'Authorization': f'Bearer {token}'
                          },
                          verify=http_config.get('verify_cert'))
        if r.status_code == 401:
            logger.error('Export failed. Unauthorized.')
            self.update_status(Status.FAILED, 'Unauthorized.')
            raise Ignore()
        if not r.ok:
            logger.error('Export failed. Error occurred.')
            self.update_status(Status.FAILED, f'Connection error occurred when fetching {handle}. '
                                              f'Response status {r.status_code}')
            raise Ignore()
        return r.json()
