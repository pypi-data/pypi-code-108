"""Entry point for the Submitter."""

import datetime
import os
import sys

import nuke

from cionuke import utils
from cionuke.components import (
    actions,
    advanced,
    autosave,
    environment,
    assets,
    frames,
    instance_type,
    metadata,
    preview,
    project,
    software,
    title,
)


# SAFE_KNOB_CHANGED calls entry.knobChanged() in a try block
# because the node is present on the render node but the
# Python module is not.
SAFE_KNOB_CHANGED = """
try:
    entry.knobChanged()
except NameError:
    pass
"""

def add_to_nodes():
    """
    Add a Conductor submitter node to the project.

    Connect selected Write nodes to the selected submitter nodes.
    If no submitter exists, build a new one.
    """

    submitters = [n for n in nuke.selectedNodes("Group") if n.knob("cio_title")]
    write_nodes = [n for n in nuke.selectedNodes("Write")]

    if not write_nodes:
        print("Select at least one Write node.")
        return

    build_new = False
    if not submitters:
        build_new = True
        submitter = nuke.createNode("Group")
        submitter.setName("Conductor")
        build_tabs(submitter)
        submitters = [submitter]

    for submitter in submitters:
        inputs = submitter.dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)
        i = len(inputs)
        for write_node in write_nodes:
            if write_node not in inputs:
                write_node.knob("selected").setValue(False)
                submitter.setInput(i, write_node)
                i += 1

    if build_new:
        submitter.knob("selected").setValue(True)
        nuke.show(submitter)
        submitter.knob("Configure").setFlag(0)


def build_tabs(submitter):
    """
    Add Conductor controls to the submitter.

    Args:
        submitter (Group node): The submitter node
    """
    config_tab = nuke.Tab_Knob("Configure")
    submitter.addKnob(config_tab)

    actions.build(submitter)
    title.build(submitter)
    project.build(submitter)
    instance_type.build(submitter)
    utils.divider(submitter, "div_1")
    software.build(submitter)
    utils.divider(submitter, "div_2")
    frames.build(submitter)
    utils.divider(submitter, "div_3")
    advanced.build(submitter)
    environment.build(submitter)
    utils.divider(submitter, "div_4")
    assets.build(submitter)
    utils.divider(submitter, "div_5")
    metadata.build(submitter)
    utils.divider(submitter, "div_6")
    autosave.build(submitter)

    preview_tab = nuke.Tab_Knob("Preview")
    submitter.addKnob(preview_tab)
    preview.build(submitter)

    submitter.knob("knobChanged").setValue(SAFE_KNOB_CHANGED)

    # Trigger a preview update now
    preview.knobChanged(submitter, submitter.knob("cio_title"))


COMPONENTS = (
    actions,
    project,
    title,
    instance_type,
    software,
    environment,
    metadata,
    assets,
    frames,
    advanced,
    autosave,
    preview,
)

def knobChanged():
    """
    Notify all component modules when a knob changes.
    """
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    for component in COMPONENTS:
        try:
            component.knobChanged(node, knob)
        except AttributeError:
            pass
