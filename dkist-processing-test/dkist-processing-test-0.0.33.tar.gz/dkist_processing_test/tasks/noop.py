"""
Test task for infrastructure integration
"""
from dkist_processing_core import TaskBase


class NoOpTask(TaskBase):
    def run(self) -> None:
        pass


class NoOpTask2(NoOpTask):
    pass
