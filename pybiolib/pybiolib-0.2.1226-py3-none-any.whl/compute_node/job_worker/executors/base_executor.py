import abc

from biolib.compute_node.job_worker.executors.types import LocalExecutorOptions


class BaseExecutor(abc.ABC):

    def __init__(self, options: LocalExecutorOptions):
        self._options: LocalExecutorOptions = options
        self._is_cleaning_up = False

    @abc.abstractmethod
    def execute_module(self, module_input_serialized: bytes) -> bytes:
        pass

    @abc.abstractmethod
    def cleanup(self) -> None:
        pass
