"""
Example valid workflow
"""
from dkist_processing_core import Workflow
from dkist_processing_core.tests.task_example import Task
from dkist_processing_core.tests.task_example import Task2
from dkist_processing_core.tests.task_example import Task3
from dkist_processing_core.tests.task_example import Task4

#        |---> Task2 --->|
# Task ->|               |----> Task4
#        |---> Task3 --->|

example = Workflow(process_category="valid", process_name="workflow", workflow_package=__package__)
example.add_node(task=Task, upstreams=None)
example.add_node(task=Task2, upstreams=Task)
example.add_node(task=Task3, upstreams=Task)
example.add_node(task=Task4, upstreams=[Task2, Task3])
