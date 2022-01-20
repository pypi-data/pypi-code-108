"""
Define the failure callback functionality
"""
import json
import logging
from contextlib import contextmanager
from os import environ
from typing import Optional
from uuid import uuid4

from talus import DurableBlockingProducerWrapper
from talus.message import message_class

logger = logging.getLogger(__name__)


@message_class(routing_key="recipe.run.failure.m", queues=["recipe.run.failure.q"])
class RecipeRunFailureMessage:
    workflowName: str
    workflowVersion: str
    taskName: str
    dagRunId: str = None
    logUrl: str = None
    conversationId: str = uuid4().hex


def _isb_connection_info() -> dict:
    try:
        mesh_config = environ["MESH_CONFIG"]
        mesh_config = json.loads(mesh_config)
        # Interservice bus
        rabbitmq_config = {
            "rabbitmq_host": mesh_config["interservice-bus"]["mesh_address"],
            "rabbitmq_port": mesh_config["interservice-bus"]["mesh_port"],
            "rabbitmq_user": environ["ISB_USERNAME"],
            "rabbitmq_pass": environ["ISB_PASSWORD"],
            "retry_tries": 5,
        }
        return rabbitmq_config
    except (KeyError, TypeError, ValueError, UnicodeDecodeError):
        logger.warning(f"Using default rabbit mq config.  Dev Only")
        default = {
            "rabbitmq_host": "127.0.0.1",
            "rabbitmq_port": 5672,
            "rabbitmq_user": "guest",
            "rabbitmq_pass": "guest",
            "retry_tries": 1,
        }
        return default


@contextmanager
def recipe_run_failure_message_producer_factory() -> DurableBlockingProducerWrapper:
    try:
        with DurableBlockingProducerWrapper(
            producer_queue_bindings=RecipeRunFailureMessage.binding(),
            publish_exchange="master.direct.x",
            **_isb_connection_info(),
        ) as producer:
            yield producer
    finally:
        pass


def parse_dag_run_id_from_context(context: dict) -> Optional[str]:
    return context.get("run_id", None)


def parse_log_url_from_context(context: dict) -> Optional[str]:
    ti = context.get("task_instance", object)
    try:
        return ti.log_url
    except AttributeError:
        return None


def chat_ops_notification(
    context: dict,
    workflow_name: str,
    workflow_version: str,
    task_name: str,
    producer_factory=recipe_run_failure_message_producer_factory,
) -> None:
    """
    Publish message with information regarding a task failure for publication to a chat service
    """
    dag_run_id = parse_dag_run_id_from_context(context)
    log_url = parse_log_url_from_context(context)
    message = RecipeRunFailureMessage(
        workflowName=workflow_name,
        workflowVersion=workflow_version,
        taskName=task_name,
        logUrl=log_url,
        dagRunId=dag_run_id,
    )

    try:
        with producer_factory() as producer:
            logger.warning(f"Publishing failure callback message: {message=}")
            return producer.publish_message(message)
    except Exception as e:
        logger.error(f"Error raised executing failure callback: {e=}")
