"""
Workflow which exercises the api's but doesn't perform an action
"""
from dkist_processing_core import Workflow

from dkist_processing_test.tasks.noop import NoOpTask
from dkist_processing_test.tasks.noop import NoOpTask2


noop = Workflow(process_category="test", process_name="noop", workflow_package=__package__)
noop.add_node(task=NoOpTask, upstreams=None)


noop_flow = Workflow(
    process_category="test", process_name="noop_flow", workflow_package=__package__
)
noop_flow.add_node(task=NoOpTask, upstreams=None)
noop_flow.add_node(task=NoOpTask2, upstreams=NoOpTask)
