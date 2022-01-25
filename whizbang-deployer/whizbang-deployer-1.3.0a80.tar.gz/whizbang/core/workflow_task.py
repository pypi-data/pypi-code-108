import datetime
from time import sleep
from abc import ABC, abstractmethod

import requests

from whizbang.util.deployment_helpers import timestamp


class IWorkflowTask(ABC):
    @abstractmethod
    def execute(self, request, output=None):
        """"""

    @abstractmethod
    def set_next(self, task: 'IWorkflowTask') -> 'IWorkflowTask':
        """"""


class WorkflowTask(IWorkflowTask):
    def __init__(self):
        self.__next: IWorkflowTask = None

    @property
    @abstractmethod
    def task_name(self) -> str:
        """"""
        raise NotImplementedError

    @abstractmethod
    def run(self, request) -> any:
        """"""
        raise NotImplementedError

    def execute(self, request, output: dict = None):
        output = output or {}
        result = self.run(request)
        output[self.task_name] = result
        

        if self.__next:
            self.__next.execute(request, output)
        return output

    def set_next(self, task: 'IWorkflowTask') -> 'IWorkflowTask':
        self.__next = task
        return self.__next
