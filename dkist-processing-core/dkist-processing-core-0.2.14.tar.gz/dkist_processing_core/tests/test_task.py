"""
Tests for the TaskBase functionality
"""
import pytest

from dkist_processing_core.task import TaskBase


def test_task_execution(task_subclass):
    """
    Given: Task subclass and parametrized APM configurations
    When: calling the instance
    Then: the run method is executed
    """
    task = task_subclass(recipe_run_id=1, workflow_name="", workflow_version="")
    task()
    assert task.pre_run_was_called
    assert task.run_was_called
    assert task.post_run_was_called


def test_task_run_failure(error_task_subclass):
    """
    Given: Task subclass and parametrized APM configurations
    When: calling the instance
    Then: the run method is executed
    """
    task = error_task_subclass(recipe_run_id=1, workflow_name="", workflow_version="")
    with pytest.raises(RuntimeError):
        task()


def test_base_task_instantiation():
    """
    Given: Abstract Base Class for a Task
    When: Instantiating base class
    Then: Receive TypeError
    """
    with pytest.raises(TypeError):
        t = TaskBase(recipe_run_id=1, workflow_name="", workflow_version="")


def test_task_subclass_instantiation(task_subclass):
    """
    Given: Subclass that implements abstract base task method(s)
    When: Instantiating subclass
    Then: Instance and Class attributes are set
    """
    recipe_run_id = 1
    workflow_name = "r2"
    workflow_version = "d2"
    task = task_subclass(
        recipe_run_id=recipe_run_id,
        workflow_name=workflow_name,
        workflow_version=workflow_version,
    )
    # class vars
    assert task.retries == task_subclass.retries
    # instance vars
    assert task.recipe_run_id == recipe_run_id
    assert task.workflow_name == workflow_name
    assert task.workflow_version == workflow_version
    # calculated instance vars
    assert task.task_name == task_subclass.__name__


def test_repr_str(task_instance):
    """
    Given:  An instance of a task
    When: accessing the string or repr
    Then: Receive a value
    """
    assert str(task_instance)
    assert repr(task_instance)
