""" Tools for working with Extender Workflows."""
try:
    from accpac import WorkflowInstance
except ImportError:
    pass

from extools.error_stack import consume_errors
from extools.view.exsql import exsql_result
from extools.view.errors import ExViewRecordDoesNotExist
from extools.message import logger_for_module

WORKFLOW_EXISTS_SQL = """
    SELECT TOP(1) WIID FROM VIWORKIH WHERE
        VIEWID = '{view}' AND
        VIEWKEY = '{view_key}'"""

WORKFLOW_STEPNAME_POST_SQL = """
        AND STEPNAME = '{step_name}'
"""

def workflow_exists(view, view_key, step_name=""):
    """Check if a workflow exists for the given view, key, and optional step.

    :param view: the View ID of the workflow, i.e. OE0520
    :type view: str
    :param view_key: the View Key for the workflow, i.e. ORD000001
    :type view_key: str
    :param step_name: the name of the step the workflow must be in. Optional.
    :type step_name: str
    :returns: True if exists, else False
    :rtype: bool
    """
    log = logger_for_module("extools")
    query = WORKFLOW_EXISTS_SQL.format(view=view, view_key=view_key)
    if step_name and step_name.strip() != "None":
        query = query + WORKFLOW_STEPNAME_POST_SQL.format(step_name=step_name)

    log.debug("workflow_exists({}, {}, {}): {}".format(view, view_key, step_name, query))

    try:
        with exsql_result(query):
            return True
    except ExViewRecordDoesNotExist:
        return False

    return True     # assume the worst.

def create_workflow_instance(template, view, view_key, entry_step,
                             viewop="", params=[], **instance_variables):
    """Create a new workflow instance.

    :param template: the workflow template to use for the instance.
    :type template: str
    :param view: the view Roto ID.
    :type view: str
    :param view_key: the view key for the instance.
    :type view_key: str
    :param entry_step: the entry step for the workflow.
    :type entry_step: str
    :param params: list of up for four positional params to set on entry step.
    :type params: str[]
    :param instance_variables: instance variables set before starting workflow.
    :returns: Workflow Instance ID (wiid)
    :rtype: int
    """
    log = logger_for_module("extools")
    log.debug("creating workflow instance {}, {}, {}, {}".format(
        template, view, view_key, entry_step))
    wiid = 0
    workflow_instance = WorkflowInstance()
    workflow_instance.start(template)
    workflow_instance.setViewID(view)
    workflow_instance.setViewKey(view_key)
    workflow_instance.viworkih.put("VIEWOP", viewop)

    for key, value in instance_variables.items():
        workflow_instance.setValue(key, value)

    workflow_instance.progressTo(entry_step, *params)

    if workflow_instance.save() == 0:
        wiid = workflow_instance.viworkih.get("WIID")
        log.info("initial save successful.")
    else:
        log.warn("initial save failed")
        log.debug_error_stack()
        errors = consume_errors()

    log.info("workflow instance {} created.".format(wiid))
    return wiid
