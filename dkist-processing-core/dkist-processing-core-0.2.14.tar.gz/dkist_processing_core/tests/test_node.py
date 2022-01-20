"""
Tests of the _node.py module
"""
import subprocess
from subprocess import CalledProcessError

import pytest
from airflow.operators.bash import BashOperator
from jinja2 import Template

from dkist_processing_core._node import Node
from dkist_processing_core.tests.task_example import Task


def test_nodes(node, fake_producer_factory):
    """
    Given: Workflow tasks to initialize a Node
    When: Initializing the Node with valid task and upstreams
    Then: Node properties are created as expected
    """
    node, task, upstream, name, version = node
    operator = node.operator
    failure_callback_func = operator.on_failure_callback
    assert callable(failure_callback_func)
    # passing in just a context dict positional arg with a fake http adapter does not raise an error
    failure_callback_func({"context": True}, producer_factory=fake_producer_factory)
    assert isinstance(operator, BashOperator)
    assert node._install_command in operator.bash_command
    assert node._python in operator.bash_command
    assert node.workflow_name == name
    assert node.upstreams == upstream
    assert node.task == task
    assert node.workflow_version == version


def test_node_bash_template_return_0(node):
    """
    Given: A valid node instance
    When: Running the bash script template WITHOUT an error producing python call
    Then: It returns a 0
    """
    node, _, _, _, _ = node
    cmd = 'python -c "pass"'
    result = subprocess.run(node._bash_template(cmd), shell=True, check=True)
    assert result.returncode == 0


def test_node_bash_template_return_1(node):
    """
    Given: A valid node instance
    When: Running the bash script template WITH an error producing python call
    Then: It returns a 1
    """
    node, _, _, _, _ = node
    cmd = 'python -c "raise Exception"'
    with pytest.raises(CalledProcessError):
        subprocess.run(node._bash_template(cmd), shell=True, check=True)


def test_node_python():
    """
    Given: Python jinja rendered with dag run data from a node instance
    When: parsing the python call
    Then: no exceptions raised
    """
    # Given
    node = Node(
        workflow_name="test_node_python",
        workflow_version="v1",
        workflow_package=__package__,
        task=Task,
    )
    code_template = Template(node._python)

    class RenderData:
        def __init__(self):
            self.conf = {"recipe_run_id": 100}

    dag_run = RenderData()
    rendered_code = code_template.render(dag_run=dag_run)

    # When
    compile(rendered_code, filename="node_test.pyc", mode="exec")
    # Then
    assert True  # exception not raised from compile


def test_invalid_node(task_subclass):
    """
    Given: An invalid task (not inheriting from TaskBase)
    When: Create a Node with that Task
    Then: Get a TypeError
    """

    class GoodTask(task_subclass):
        pass

    class BadTask:
        pass

    with pytest.raises(TypeError):
        Node(workflow_name="bad_task", workflow_package=__package__, task=BadTask)

    with pytest.raises(TypeError):
        Node(
            workflow_name="bad_upstream",
            workflow_package=__package__,
            task=GoodTask,
            upstreams=BadTask,
        )

    with pytest.raises(TypeError):
        Node(
            workflow_name="bad_upstream2",
            workflow_package=__package__,
            task=GoodTask,
            upstreams=[GoodTask, BadTask],
        )
