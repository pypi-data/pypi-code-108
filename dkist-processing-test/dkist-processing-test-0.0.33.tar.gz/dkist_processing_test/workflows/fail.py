"""
Workflow which is designed to fail
"""
from dkist_processing_core import Workflow

from dkist_processing_test.tasks.fail import FailTask


fail = Workflow(process_category="test", process_name="fail", workflow_package=__package__)
fail.add_node(task=FailTask, upstreams=None)
