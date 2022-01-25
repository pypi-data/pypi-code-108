from abc import ABC, abstractmethod

from whizbang.core.workflow_task import IWorkflowTask


class IWorkflow(ABC):
    """the workflow interface"""

    @abstractmethod
    def run(self, request) -> any:
        """"""


class Workflow(IWorkflow):
    @abstractmethod
    def _get_workflow_tasks(self) -> 'list[IWorkflowTask]':
        """abstract workflow method should return an IWorkflowTask"""
        raise NotImplementedError

    def run(self, request) -> any:
        workflow_tasks = self._get_workflow_tasks()
        for idx, task in enumerate(workflow_tasks):
            if (idx + 1) == len(workflow_tasks):
                break
            task.set_next(workflow_tasks[idx + 1])

        first_task = workflow_tasks[0]
        output = first_task.execute(request)
        result = self._process_output(output)
        return result

    def _process_output(self, result: dict) -> any:
        """override if needed"""
        return result
