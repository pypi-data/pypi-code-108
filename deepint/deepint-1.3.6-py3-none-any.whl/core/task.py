#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import time
import enum
import asyncio
from datetime import datetime
from typing import Any, List, Dict

from ..auth import Credentials
from ..error import DeepintTaskError
from ..util import handle_request, parse_date, parse_url


class TaskStatus(enum.Enum):
    """Available task status in the system.
    """
    pending = 0
    running = 1
    failed = 2
    success = 3
    unknown = 4

    @classmethod
    def from_string(cls, _str: str) -> 'TaskStatus':
        """Builds the :obj:`deepint.core.task.TaskStatus` from a :obj:`str`.

        Args:
            _str: name of the task status.

        Returns:
            the task status converted to :obj:`deepint.core.task.TaskStatus`.
        """

        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def all(cls) -> List[str]:
        """ Returns all available task status serialized to :obj:`str`.

        Returns:
            all available task status
        """

        return [e.name for e in cls]


class TaskInfo:
    """Stores the information of a Deep Intelligence task.
    
    Attributes:
        task_id: task's id in format uuid4.
        name: task's name.
        description: task's description.
        user_id: id of the user who created the task
        user_name: user who created the task
        created: task creation date
        status: task status. (pending = Pending to be handled, running = Executing, success = Ended successfully, failed = Ended with an error)
        duration: duration of the task (in milliseconds)
        progress: progress of the current sub-task
        subtask: name of the current sub-task
        result: id of the resulting object of the task
        result_type: type of the resulting object of the task (source or model).
        error_code:  error code (if the task failed)
        error_description: error message (if the task failed)
    """

    def __init__(self, task_id: str, user_id: str, user_name: str, created: datetime, status: TaskStatus, duration: int,
                 name: str, description: str, progress: int, subtask: str, result: str, result_type: str,
                 error_code: str, error_description: str) -> None:
        self.task_id = task_id
        self.user_id = user_id
        self.user_name = user_name
        self.created = created
        self.status = status
        self.duration = duration
        self.name = name
        self.description = description
        self.progress = progress
        self.subtask = subtask
        self.result = result
        self.result_type = result_type
        self.error_code = error_code
        self.error_description = error_description

    def __eq__(self, other):
        if not isinstance(other, TaskInfo):
            return False
        else:
            return self.task_id == other.task_id

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

    @staticmethod
    def from_dict(obj: Any) -> 'TaskInfo':
        """Builds a TaskInfo with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized TaskInfo.

        Returns:
            TaskInfo containing the information stored in the given dictionary.
        """

        task_id = obj.get("id")
        user_id = obj.get("user_id")
        user_name = obj.get("user_name")
        created = parse_date(obj.get("created"))
        status = TaskStatus.from_string(obj.get("status"))
        duration = int(obj.get("duration"))
        name = obj.get("name")
        description = obj.get("description")
        progress = int(obj.get("progress"))
        subtask = obj.get("subtask")
        result = obj.get("result")
        result_type = obj.get("result_type")
        error_code = obj.get("error_code")
        error_description = obj.get("error_description")
        return TaskInfo(task_id, user_id, user_name, created, status, duration, name, description, progress, subtask,
                        result,
                        result_type, error_code, error_description)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.task_id, "user_id": self.user_id, "user_name": self.user_name,
                "created": self.created.isoformat(), "status": self.status.name, "duration": self.duration,
                "name": self.name, "description": self.description, "progress": self.progress,
                "subtask": self.subtask, "result": self.result, "result_type": self.result_type,
                "error_code": self.error_code, "error_description": self.error_description}


class Task:
    """A Deep Intelligence task.
    
    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.task.Task.build`
    or :obj:`deepint.core.task.Task.from_url` methods. 
    
    Attributes:
        organization_id: the organziation where task is located.
        workspace_id: workspace where task is located.
        info: :obj:`deepint.core.task.TaskInfo` to operate with task's information.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the task. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, organization_id: str, workspace_id: str, credentials: Credentials, info: TaskInfo) -> None:
        self.credentials = credentials
        self.info = info
        self.workspace_id = workspace_id
        self.organization_id = organization_id

    def __str__(self):
        return f'<Task organization_id={self.organization_id} workspace={self.workspace_id} {self.info}>'

    @classmethod
    def build(cls, organization_id: str, workspace_id: str, task_id: str, credentials: Credentials = None) -> 'Task':
        """Builds a task.
        
        Note: when task is created, the task's information is retrieved from API.

        Args:
            organization_id: organization where task is located.
            workspace_id: workspace where task is located.
            task_id: task's id.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the task. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the task build with the given parameters and credentials.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        info = TaskInfo(task_id=task_id, user_id=None, user_name=None, created=None, status=None, duration=None,
                        name=None,
                        description=None, progress=None, subtask=None, result=None, result_type=None, error_code=None,
                        error_description=None)
        task = cls(organization_id=organization_id, workspace_id=workspace_id, credentials=credentials, info=info)
        task.load()
        return task

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Task':
        """Builds a task from it's API or web associated URL.

        The url must contain the workspace's id and the task's id as in the following examples:

        Example:
            - https://app.deepint.net/o/3a874c05-26d1-4b8c-894d-caf90e40078b/workspace?ws=f0e2095f-fe2b-479e-be4b-bbc77207f42d&s=task&i=db98f976-f4bb-43d5-830e-bc18a3a89641
            - https://app.deepint.net/api/v1/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42/task/db98f976-f4bb-43d5-830e-bc18a3a89641
        
        Note: when task is created, the task's information and features are retrieved from API.
            Also it is remmarkable that if the API URL is providen, the organization_id must be provided in the optional parameter, otherwise
            this ID won't be found on the URL and the Organization will not be created, raising a value error.

        Args:
            url: the task's API or web associated URL.
            organization_id: the id of the organziation. Must be providen if the API URL is used.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the task. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the task build with the URL and credentials.
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError('Fields organization_id must be in url to build the object. Or providen as optional parameter.')

        if 'workspace_id' not in url_info or 'task_id' not in url_info:
            raise ValueError('Fields workspace_id and task_id must be in url to build the object.')

        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        # create new credentials
        new_credentials = Credentials(token=credentials.token, instance=hostname)
        
        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'], task_id=url_info['task_id'], 
                credentials=new_credentials)

    def load(self):
        """Loads the task's information.

        If the task's information is already loaded, is replace by the new one after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/task/{self.info.task_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # map results
        self.info = TaskInfo.from_dict(response)

    def delete(self):
        """Deletes the task.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/task/{self.info.task_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='DELETE', path=path, headers=headers, credentials=self.credentials)

    def resolve(self, raise_on_error=True, poll_interval: int = 3):
        """Waits for the task to be finished
        
        Args:
            raise_on_error: if set to True and the task enters in an errored status, a :obj:`deepint.error.errors.DeepintTaskError` is raised.
                In other case, if the task enters in an errored state, the wait for task process will stop and the error will not be raised. 
            poll_interval: Number of seconds between task status checks (it consists in a query to API). If not provided the default value is 3.
        """

        self.load()
        while self.info.status == TaskStatus.pending or self.info.status == TaskStatus.running:
            time.sleep(poll_interval)
            self.load()

        if raise_on_error and self.is_errored():
            raise DeepintTaskError(task=self.info.task_id, name=self.info.name, code=self.info.error_code,
                                   message=self.info.error_description)

    def fetch_result(self, force_reload=False) -> Dict[str, str]:
        """Retrieves the result of the task.
        
        Args:
            force_reload: if set to True the task information is reloaded, then the result is fetched.

        Returns:
            the result generated by the task in deepint.net
        """
        
        if force_reload:
            self.load()

        return {self.info.result_type: self.info.result}

    def is_errored(self, force_reload=False) -> bool:
        """Checks if the task has failed.
        
        Args:
            force_reload: if set to True the task information is reloaded, then the status is checked.

        Returns:
            True if task has entered in error state or False in other case.
        """

        if force_reload:
            self.load()

        return self.info.status == TaskStatus.failed

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"info": self.info.to_dict()}
