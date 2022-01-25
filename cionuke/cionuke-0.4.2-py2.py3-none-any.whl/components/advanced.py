"""
Controls that are beyond basic operation.
"""
import nuke
import re
import os

from cionuke import utils
from cionuke import const as k

from ciopath.gpath_list import PathList

DEFAULT_TASK_TEMPLATE = 'nuke -V 2 --remap "[value cio_pathmap]" -F [value cio_range_args] -X [python {",".join([n.name() for n in nuke.thisNode().dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)])}] "[regsub -nocase {^[A-Z]:} [value root.name] []]"'


USE_DAEMON_TOOLTIP = """
An upload daemon is a separate background process that uploads files outside of Nuke. It means the 
submission in Nuke is not blocked while assets are uploaded. If you turn this option on, you'll need
to run conductor uploader in a terminal window / command prompt.
"""

EMAILS_TOOLTIP = """
A comma separated list of emails to be notified when the job completes.
"""

RETRIES_TOOLTIP = """
Long running jobs may be stopped if a preemptible instance type is selected. This setting specifies
how many times to restart the task if preempted.
"""

TASK_TOOLTIP = """
A template which is used to generate the Nuke render command to run on remote instances. The default template uses an expression as broken down below.

<strong>nuke -V 2</strong> : The nuke command in very verbose mode.

<strong>--remap "[value cio_pathmap]"</strong> : A list of path mappings to strip away Windows drive letters, since Conductor render nodes run on linux. "cio_pathmap" is a hidden property that is updated before submission based on the asset paths in use.

<strong>-F [value cio_range_args]</strong> : specifies the frame range to render for each task. "cio_range_args" is a hidden property that is updated for every chunk while generating the submission payload.

<strong>-X [python {",".join([n.name() for n in nuke.thisNode().dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)])}]</strong> : This python snippet generates a comma separated list of Write nodes to be rendered.

<strong>"[regsub -nocase {^[A-Z]:} [value root.name] []]"</strong> : The filename. On windows, the drive letter is stripped by the regsub TCL expression.

If you examine the task template and then check the tasks_data section of the Preview tab, you'll see how it is resolved.
"""

USE_CUSTOM_TASK_TOOLTIP= """
This option allows you to customize the nuke command that is run for each task. To use it, you should be comfortable writing TCL expressions.
"""

LOCATION_TOOLTIP = """
Set a location tag for the purpose of matching to an uploader or downloader process.
If your organization is distributed in several locations, you can enter a value here, for example, London. 
Then when you run a downloader daemon you can add the location option to limit downloads to only those that were submitted in London.
"""

def build(submitter):
    """
    Build the controls.
    """
    knob = nuke.Boolean_Knob("cio_use_daemon", "Use upload daemon")
    knob.setTooltip(USE_DAEMON_TOOLTIP)
    submitter.addKnob(knob)
    knob.setValue(0)

    knob = nuke.String_Knob("cio_emails", "Email notifications", "you@vfxco.com,me@vfxco.com")
    knob.setTooltip(EMAILS_TOOLTIP)
    submitter.addKnob(knob)
    knob.setEnabled(False)

    knob = nuke.Boolean_Knob("cio_use_emails", "Enable")
    knob.clearFlag(nuke.STARTLINE)
    submitter.addKnob(knob)
    knob.setValue(0)

    knob = nuke.Int_Knob("cio_retries", "Retries on preemption")
    knob.setValue(1)
    knob.setTooltip(RETRIES_TOOLTIP)
    knob.setFlag(nuke.STARTLINE)
    submitter.addKnob(knob)

    nuke.knobDefault("Group.cio_task", DEFAULT_TASK_TEMPLATE)
    knob = nuke.EvalString_Knob("cio_task", "Task template")
    knob.setValue(DEFAULT_TASK_TEMPLATE)
    knob.setTooltip(TASK_TOOLTIP)
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.Boolean_Knob("cio_use_custom_task", "Use custom task")
    knob.clearFlag(nuke.STARTLINE)
    knob.setTooltip(USE_CUSTOM_TASK_TOOLTIP)
    submitter.addKnob(knob)
    knob.setValue(0)

    # Hidden - holds range args for each task, e.g. 1-5
    knob = nuke.String_Knob("cio_range_args", "Range args")
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.String_Knob("cio_location", "Location")
    knob.setTooltip(LOCATION_TOOLTIP)
    submitter.addKnob(knob)

    if k.FEATURE_DEV:
        utils.divider(submitter, "advanced1")
        knob = nuke.Boolean_Knob("cio_use_fixtures", "Use fixtures")
        submitter.addKnob(knob)
        knob.setValue(0)

    utils.divider(submitter, "advanced2")

    knobChanged(submitter, submitter.knob("cio_use_custom_task"))


def knobChanged(node, knob):
    """
    Adjust the enabled/visible state of widgets in this component.
    """
    knob_name = knob.name()
    if knob_name in ["cio_use_emails", "cio_use_custom_task"]:
        use_emails = bool(node.knob("cio_use_emails").getValue())
        node.knob("cio_emails").setEnabled(use_emails)

        use_custom_task = bool(node.knob("cio_use_custom_task").getValue())
        node.knob("cio_task").setVisible(use_custom_task)

        # reset the task expression when switching off use_custom
        if not use_custom_task:
            node.knob("cio_task").setValue(DEFAULT_TASK_TEMPLATE)


def resolve(submitter, **kwargs):
    """
    Resolve the part of the payload that is handled by this component.
    """
    result = {}
    result["autoretry_policy"] = {"preempted": {"max_retries": int(submitter.knob("cio_retries").getValue())}}
    result["local_upload"] = not submitter.knob("cio_use_daemon").getValue()

    location = submitter.knob("cio_location").getValue().strip()
    if location:
        result["location"] = location

    if submitter.knob("cio_use_emails").getValue():
        emails = list([_f for _f in re.split(r"[, ]+", submitter.knob("cio_emails").getValue()) if _f])
        if emails:
            result["notify"] = emails
    try:
        result["output_path"] = evaluate_output_path(submitter)
    except BaseException:
        result["output_path"] = "Invalid output paths"
    return  result


def evaluate_output_path(submitter):
    """
    Output path is calculated as the common ancestor path of connected Write nodes. 

    Returns:
        [string]: A path
    """
    path_list = PathList()
    for node in [n for n in submitter.dependencies() if n.Class() == "Write"]:
        value = utils.as_globbable_path(node.knob("file"))
        value = os.path.dirname(value)
        value = utils.truncate_path_to_star(value)
        if value:
            path_list.add(value)
    return path_list.common_path().fslash()

def affector_knobs():
    """
    Register knobs in this component that affect the payload.
    """
    return [
        "cio_use_daemon",
        "cio_emails",
        "cio_use_emails",
        "cio_retries",
        "cio_use_custom_task",
        "cio_task",
        "cio_location"
    ]
