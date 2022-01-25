"""
Manage the autosave template.
"""
import nuke
import re
from cionuke import utils

DEFAULT_AUTOSAVE_TEMPLATE = "[file dirname [value root.name]]/cio_[file tail [value root.name]]"


def build(submitter):
    """
    Build the controls
    """
    nuke.knobDefault("Group.cio_autosave_template", DEFAULT_AUTOSAVE_TEMPLATE)
    autosave_template_knob = nuke.EvalString_Knob("cio_autosave_template", "Autosave filename")
    submitter.addKnob(autosave_template_knob)
    autosave_template_knob.setValue(DEFAULT_AUTOSAVE_TEMPLATE)

    do_autosave_knob = nuke.Boolean_Knob("cio_do_autosave", "Do Autosave")
    do_autosave_knob.clearFlag(nuke.STARTLINE)
    submitter.addKnob(do_autosave_knob)
    do_autosave_knob.setValue(1)
    knobChanged(submitter,  submitter.knob("cio_do_autosave"))


def knobChanged(node, knob):
    """
    Adjust the enabled/visible state of UI components in this component.
    """
    if knob.name() == "cio_do_autosave":
        value = bool(node.knob("cio_do_autosave").getValue())
        node.knob("cio_autosave_template").setEnabled(value)

def resolve(node, **kwargs):
    return {}

def affector_knobs():
    return []
