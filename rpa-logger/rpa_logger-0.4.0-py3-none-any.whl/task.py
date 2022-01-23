'''Constants and helpers for describing RPA tasks and their status.
'''
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Hashable, List, Union
from uuid import uuid4

from .utils import timestamp
from .utils.output import OutputText

STARTED = 'STARTED'
SUCCESS = 'SUCCESS'
IGNORED = 'IGNORED'
FAILURE = 'FAILURE'
ERROR = 'ERROR'
SKIPPED = 'SKIPPED'

STATUSES = (STARTED, SUCCESS, IGNORED, FAILURE, ERROR, SKIPPED,)


@dataclass
class BaseTask:
    '''Base class to define common functionality of `rpa_logger.task.Task` and
    `rpa_logger.task.TaskSuite`
    '''
    type: str
    '''Used to identify task type, when task is presented as dict'''
    name: Union[str, None]
    '''Human-readable name of the task.'''
    status: str
    '''Describes state of the task. For example `SUCCESS` or `ERROR`.'''
    started: str
    '''UTC ISO-8601 timestamp that stores the start time of the task.
    Defined automatically when instance is created.
    '''
    finished: Union[str, None]
    '''UTC ISO-8601 timestamp that stores the finish time of the task.
    Defined automatically when `rpa_logger.task.BaseTask.finish` method is
    called.
    '''
    metadata: Dict[str, Any]
    '''Container for any other data stored in the task. Could, for example,
    contain information about the execution environment or data that was
    processed in the task.
    '''

    def __init__(self, name: Union[str, None], status: str = STARTED) -> None:
        '''
        Args:
            name: Name of the task.
            status: Status to use for the started task.
        '''
        self.status = status
        self.name = name
        self.started = timestamp()
        self.finished = None
        self.metadata = dict()

    def finish(self, status) -> None:
        '''Set finished timestamp and end status of the task

        Args:
            status: Status to use for the finished task.
        '''
        self.status = status
        self.finished = timestamp()

    def log_metadata(self, key: str, value: Any) -> None:
        '''Log metadata for the task.

        Args:
            key: Key for the metadata item.
            value: Value for the metadata item. If task data is saved as json
                or yaml, this value must be serializable.
        '''
        self.metadata[key] = value


@dataclass
class Task(BaseTask):
    '''Defines single task and stores its output and metadata
    '''
    output: List[OutputText]

    def __init__(self, name: str, status: str = STARTED):
        '''
        Args:
            name: Name of the task.
            status: Status to use for the started task.
        '''
        super().__init__(name, status)
        self.output = list()

    @property
    def type(self):
        return 'TASK'

    def log_output(self, text: str, stream: str = 'stdout') -> None:
        '''Append new `rpa_logger.utils.output.OutputText` to task output.

        Args:
            text: Output text content.
            stream: Output stream. Defaults to `stdout`.
        '''
        self.output.append(OutputText(text, stream))


@dataclass
class TaskSuite(BaseTask):
    '''Defines task suite and stores its tasks and metadata
    '''
    description: Union[str, None]
    tasks: List[Task]

    def __init__(
            self,
            name: Union[str, None],
            description: str = None,
            status: str = STARTED):
        '''
        Args:
            name: Name of the task suite.
            description: Description of the task suite.
            status: Status to use for the started task suite.
        '''
        super().__init__(name, status)
        self.description = description
        self._tasks: Dict[Hashable, Task] = dict()

    @property
    def type(self):
        return 'SUITE'

    @property
    def tasks(self) -> List[Task]:  # pylint: disable=function-redefined
        '''Return suites tasks as list sorted by the started time.
        '''
        tasks = list(self._tasks.values())
        tasks.sort(key=lambda i: i.started)
        return tasks

    @property
    def active_tasks(self) -> List[Task]:
        '''Return suites active tasks as list sorted by the started time.

        Task is active until it is finished; Task is active, if its finished
        variable is None.
        '''
        return [i for i in self.tasks if i.finished is None]

    @property
    def task_status_counter(self) -> Counter:
        '''Return `Counter` instance initialized with suites task statuses.
        '''
        return Counter(i.status for i in self._tasks.values())

    def create_task(
            self,
            name: str,
            key: Hashable = None,
            status: str = STARTED):
        '''Create new task and store it in the suite tasks.

        Args:
            name: Name of the task.
            key: Key to identify the created task with.
            status: Status to use for the started task.

        Returns:
            Key of the created task.
        '''
        if not key:
            key = uuid4()

        self._tasks[key] = Task(name, status)
        return key

    def log_task(self, status: str, name: str) -> None:
        '''Create and finish a new task.

        Args:
            name: Name of the task.
            status: Status to use for the finished task.

        Returns:
            Key of the created task.
        '''
        key = self.create_task(name)
        self.finish_task(key, status)
        return key

    def finish_task(self, key: Hashable, status: str) -> None:
        '''Set finished timestamp and end status of the task

        Args:
            key: Key of the task to finish
            status: Status to use for the finished task.
        '''
        return self._tasks[key].finish(status)

    def get_task(self, key: Hashable) -> Task:
        '''Get `rpa_logger.task.Task` with given key.

        Args:
            key: Key to try to find from suite.

        Returns:
            Task with matching key.
        '''
        return self._tasks.get(key)

    def log_metadata(
            self,
            key: str,
            value: Any,
            task_key: Hashable = None) -> None:
        '''Log metadata into the task suite or any of its tasks.

        Args:
            key: Key for the metadata item.
            value: Value for the metadata item. If task data is saved as json
                or yaml, this value must be serializable.
            task_key: Key of a task to log metadata into. If None, metadata
                is logged to the suite.
        '''
        if task_key:
            self._tasks[task_key].log_metadata(key, value)

        super().log_metadata(key, value)

    def log_output(self, key: Hashable, text: str,
                   stream: str = 'stdout') -> None:
        '''Append new `rpa_logger.utils.output.OutputText` to task output.

        Args:
            key: Key of the task to log output to.
            text: Output text content.
            stream: Output stream. Defaults to `stdout`.
        '''
        self._tasks[key].log_output(text, stream)
