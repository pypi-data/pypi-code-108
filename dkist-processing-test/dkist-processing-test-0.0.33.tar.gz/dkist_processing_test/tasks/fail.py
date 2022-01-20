"""
Test task for infrastructure integration that will always fail
"""
from dkist_processing_core import TaskBase


class FailTask(TaskBase):
    def run(self) -> None:
        raise RuntimeError("Failure is guaranteed")
