import nuke

import json

"""
The metadata widget.

The widget is a chunk of Qt embedded in Nuke's properties panel.
"""

from cionuke.components.conductor_knob import ConductorKnob
from cionuke.widgets.key_value_grp import KeyValueGrpList

import json
import nuke


class MetadataKnob(ConductorKnob):

    def __init__(self, submitter):
        """Set up the UI.

        Use a KeyValueGrp to hold keys and values.
        """

        super(MetadataKnob, self).__init__(submitter)

        self.component = KeyValueGrpList()
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
            entries = json.loads(self.submitter.knob(
                "cio_metadata").getText())
        except ValueError:
            entries = []
        self.component.set_entries(entries)

    def on_edited(self):
        """Update the value in the hidden storage knob."""
        payload = json.dumps(self.component.entries())
        self.submitter.knob("cio_metadata").setValue(payload)


def build(submitter):
    """Build custom k/v pair knob."""
    cmd = "metadata.MetadataKnob(nuke.thisNode())"

    knob = nuke.String_Knob("cio_metadata", "Metadata Raw", "")
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.EvalString_Knob("cio_metadata_evaluator", "MetadataEval", "")
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.PyCustom_Knob(
        "cio_metadata_ui", "Metadata",  cmd)
    knob.setFlag(nuke.STARTLINE)
    submitter.addKnob(knob)



def resolve(submitter, **kwargs):
    """Gather up metadata k/v pairs.
    
    Values can be TCL expressions.
    """
    jsonval = submitter.knob("cio_metadata").getValue() or "{}"
    metadata = json.loads(jsonval)
    eval_knob = submitter.knob("cio_metadata_evaluator")
    result = {}
    for row in metadata:
        name, value = row
        eval_knob.setValue(value)
        value = eval_knob.getValue()
        if name and value:
            result[name] = value
    return {"metadata":result }


def affector_knobs():
    return [
        "cio_metadata"
    ]