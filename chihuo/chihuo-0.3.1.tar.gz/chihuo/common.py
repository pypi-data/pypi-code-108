from typing import Union
from enum import Enum

SERVER_DEFAULT_CONFIG_PATH = "server.config"

TaskId = Union[str, bytes]


class TaskType(Enum):
    Task = "task"
    Start = "start"
    TaskLoop = "task_loop"
    SendBack = "send_back"
    Handler = "handler"
    Final = "final"


class Direction(Enum):
    Forward = 0
    Reverse = 1
