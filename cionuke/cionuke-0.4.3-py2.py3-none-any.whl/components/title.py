import nuke

CIO_TITLE_TOOLTIP = """
The title that identifies the job in the Conductor dashboard. You may use TCL expressions here.
"""

def build(submitter):
    """Build knobs to specify the job title."""
    knob_name = "cio_title"
    knob = nuke.EvalString_Knob(knob_name, "Job title", "NUKE [file tail [value root.name]]")
    knob.setTooltip(CIO_TITLE_TOOLTIP)
    submitter.addKnob(knob)


def resolve(node, **kwargs):
    return {"job_title": node.knob("cio_title").getValue()}


def affector_knobs():
    """Knobs that affect the payload when changed."""
    return ["cio_title"]


