"""
Test for the the failure callback function
"""
import json
from os import environ

import pika
import pytest

from dkist_processing_core._failure_callback import _isb_connection_info
from dkist_processing_core._failure_callback import chat_ops_notification
from dkist_processing_core._failure_callback import parse_dag_run_id_from_context
from dkist_processing_core._failure_callback import parse_log_url_from_context
from dkist_processing_core._failure_callback import recipe_run_failure_message_producer_factory
from dkist_processing_core._failure_callback import RecipeRunFailureMessage


@pytest.fixture()
def context(task_instance) -> dict:
    """
    Example task instance context dict
    """
    return {"context": True, "run_id": "QAZXYV_1", "task_instance": task_instance}


@pytest.fixture(params=["without_env_vars", "with_env_vars"])
def env_vars(request):
    """
    Fixture setting or not setting env vars
    """
    if request.param == "with_env_vars":
        environ["MESH_CONFIG"] = json.dumps(
            {"interservice-bus": {"mesh_address": "127.0.0.1", "mesh_port": 5672}}
        )
        environ["ISB_USERNAME"] = "guest"
        environ["ISB_PASSWORD"] = "guest"
        return
    try:
        environ.pop("MESH_CONFIG")
    except KeyError:
        pass
    try:
        environ.pop("ISB_USERNAME")
    except KeyError:
        pass
    try:
        environ.pop("ISB_PASSWORD")
    except KeyError:
        pass


def test_recipe_run_failure_producer_factory(env_vars):
    """
    Given: recipe_run_failure_producer_factory
    When: retrieving an producer from the factory
    Then: it is an instance of a talus.DurableBlockingProducerWrapper
    """
    with pytest.raises(pika.exceptions.AMQPConnectionError):
        recipe_run_failure_message_producer_factory().__enter__()


def test_parse_dag_run_id_from_context(context):
    """
    Given: a context dictionary
    When: parsing the context dict
    Then: run_id is extracted and returned
    """
    actual = parse_dag_run_id_from_context(context)
    assert actual == context["run_id"]


def test_parse_log_url_from_context(context):
    """
    Given: a context dictionary
    When: parsing the context dict
    Then: run_id is extracted and returned
    """
    actual = parse_log_url_from_context(context)
    assert actual == context["task_instance"].log_url


def test_isb_connection_info(env_vars):
    """
    Given: connection info function
    When: calling the function
    Then: no errors raised when env vars do not exist
    """
    conn_info = _isb_connection_info()
    assert isinstance(conn_info, dict)


def test_chat_ops_notification(fake_producer_factory, context):
    """
    Given: A fake producer factory to capture the publish from a chat ops notification
       and fake parameters
    When: call is made to chat ops notification
    Then: Expected message was published
    """
    workflow_name = "wkflow"
    workflow_version = "ver"
    task_name = "task"
    message = chat_ops_notification(
        context=context,
        workflow_name=workflow_name,
        workflow_version=workflow_version,
        task_name=task_name,
        producer_factory=fake_producer_factory,
    )
    assert isinstance(message, RecipeRunFailureMessage)
    assert message.workflowName == workflow_name
    assert message.workflowVersion == workflow_version
    assert message.taskName == task_name
    assert message.logUrl == context["task_instance"].log_url
    assert message.conversationId
    assert message.dagRunId == context["run_id"]


def test_chat_ops_notification_no_raise():
    """
    Given: chat_ops_notification function
    When: call is made to chat ops notification
    Then: No error raised
    """
    workflow_name = "wkflow"
    workflow_version = "ver"
    task_name = "task"
    context = {"context": True, "run_id": "QAZXYV_1"}
    # no errors raised
    chat_ops_notification(
        context=context,
        workflow_name=workflow_name,
        workflow_version=workflow_version,
        task_name=task_name,
    )
