"""
Abstraction layer to construct a workflow node using and airflow operator
"""
from collections.abc import Iterable
from typing import List
from typing import Tuple
from typing import Type
from typing import Union

from airflow.operators.bash import BashOperator

from dkist_processing_core.task import TaskBase


task_type_hint = Type[TaskBase]
upstreams_type_hint = Union[List[Type[TaskBase]], None, Type[TaskBase]]


class Node:
    """
    Abstraction to create a node in the workflow graph as implemented by engine api (airflow)
    """

    def __init__(
        self,
        workflow_name: str,
        workflow_version: str,
        workflow_package: str,
        task: task_type_hint,
        upstreams: upstreams_type_hint = None,
    ):
        # Task type checking
        upstreams = upstreams or []
        if not isinstance(upstreams, Iterable):
            upstreams = [
                upstreams,
            ]
        if not all([issubclass(t, TaskBase) for t in [task] + upstreams]):
            raise TypeError(
                "Only task classes inheriting from "
                "dkist_processing_core.TaskBase can be added to a workflow"
            )

        self.workflow_name = workflow_name
        self.workflow_version = workflow_version
        self.task = task
        self.workflow_package = workflow_package
        self.upstreams = upstreams

    @property
    def operator(self) -> BashOperator:
        """
        Native engine node
        """
        from datetime import timedelta
        from dkist_processing_core._failure_callback import chat_ops_notification
        from functools import partial

        return eval(self.operator_definition)

    @property
    def operator_definition(self) -> str:
        return f"""BashOperator(
    task_id='{self.task.__name__}',
    bash_command='''{self._bash_script}''',
    retries={self.task.retries},
    retry_delay=timedelta(seconds={self.task.retry_delay_seconds}),
    on_failure_callback=partial(
        chat_ops_notification,
        workflow_name='{self.workflow_name}',
        workflow_version='{self.workflow_version}',
        task_name='{self.task.__name__}'
    ),
    owner="DKIST Data Center",
)
"""

    @property
    def dependencies(self) -> List[Tuple[str, str]]:
        """
        List of upstream, downstream task name tuples
        """
        return [(upstream.__name__, self.task.__name__) for upstream in self.upstreams]

    @property
    def _bash_script(self) -> str:
        """
        Format bash script for the BashOperator
        """
        command = f"""{self._install_command}
{self._run_command}"""
        return self._bash_template(command)

    @staticmethod
    def _bash_template(command: str) -> str:
        return f"""#!/bin/bash
echo Working Directory
pwd
echo Host Python Environment i.e. system-site-packages
pip list
echo Creating Virtual Environment
python3 -m venv --system-site-packages .task_venv
echo Activate Environment
. .task_venv/bin/activate
echo Python Interpreter Location
which python
echo Run Main Command
{command}
export exit_code=$?
echo Deactivate Environment
deactivate
echo Remove Virtual Environment
rm -rf .task_venv
echo Exit with code from main command: $exit_code
exit $exit_code"""

    @property
    def _install_command(self) -> str:
        repo_name = self.workflow_package.split(".")[0].replace("_", "-")
        version = self.workflow_version
        return f"python -m pip install {repo_name}=={version}"

    @property
    def _run_command(self) -> str:
        return f'python -c "{self._python}"'

    @property
    def _python(self) -> str:
        return f"""from {self.task.__module__} import {self.task.__name__}
with {self.task.__name__}(recipe_run_id={{{{dag_run.conf['recipe_run_id']}}}}, workflow_name='{self.workflow_name}', workflow_version='{self.workflow_version}') as task:
    task()
"""
