import nuke
from ciocore import data as coredata
from ciocore.package_environment import PackageEnvironment

"""
The Extra environment widget.

The widget is a chunk of Qt embedded in Nuke's properties panel.
"""
from cionuke.components.conductor_knob import ConductorKnob
from cionuke.widgets.key_value_grp import KeyValueGrpList

import json
import nuke


class EnvironmentKnob(ConductorKnob):
    def __init__(self, submitter):
        """Set up the UI.

        Use a KeyValueGrp to hold key, value, and exclusive flags.
        """

        super(EnvironmentKnob, self).__init__(submitter)

        self.component = KeyValueGrpList(checkbox_label="Excl", key_label="Name")
        self.content_layout.addWidget(self.component)
        self.configure_signals()

    def configure_signals(self):
        self.component.edited.connect(self.on_edited)

    def updateValue(self):
        """
        Populate the UI from the hidden storage knob.

        Called automatically by Nuke when needed.
        """
        try:
            entries = json.loads(self.submitter.knob("cio_environment").getText())
        except ValueError:
            entries = []
        self.component.set_entries(entries)

    def on_edited(self):
        """Update the value in the hidden storage knob."""
        payload = json.dumps(self.component.entries())
        self.submitter.knob("cio_environment").setValue(payload)


def build(submitter):
    """
    Build custom UI knob and a string knob for storage.

    The storage knob contains JSON.
    """
    cmd = "environment.EnvironmentKnob(nuke.thisNode())"

    knob = nuke.String_Knob("cio_environment", "Environment Raw", "")
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.EvalString_Knob("cio_env_evaluator", "EnvEval", "")
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.PyCustom_Knob("cio_environment_ui", "Environment", cmd)
    knob.setFlag(nuke.STARTLINE)
    submitter.addKnob(knob)


def affector_knobs():
    """knobs that affect the payload."""
    return ["cio_environment"]


def resolve(submitter, **kwargs):
    """
    Resolve the part of the payload that is handled by this component.
    """

    extra_env = _get_extra_env(submitter)
    package_env = _get_software_package_env(submitter)
    package_env.extend(extra_env)
    return {"environment": dict(package_env)}


def _get_extra_env(submitter):
    jsonval = submitter.knob("cio_environment").getValue() or "[]"
    env = json.loads(jsonval)
    eval_knob = submitter.knob("cio_env_evaluator")
    result = []
    for row in env:
        name, value, exclusive = row
        eval_knob.setValue(value)
        value = eval_knob.getValue()
        if name and value:
            result.append(
                {
                    "name": name,
                    "value": value,
                    "merge_policy": "exclusive" if exclusive else "append",
                }
            )
    return result


def _get_software_package_env(submitter):
    result = PackageEnvironment()
    if not coredata.valid():
        return result

    tree_data = coredata.data()["software"]
    selected = submitter.knob("cio_software").value()
    package = tree_data.find_by_path(selected)
    if not package:
        return result
    result.extend(package)

    return result
