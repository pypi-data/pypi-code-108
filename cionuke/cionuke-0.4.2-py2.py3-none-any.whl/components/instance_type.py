import nuke
import json
from ciocore import data as coredata
from cionuke import const as k

TOOLTIPS = {
    "cio_insttype": "Choose a machine spec to run the job. To avoid unwanted costs, dont choose a GPU enabled machine if your script diesn't make use of a graphics card.",
    "cio_preemptible": 'Preemptible instances are lower cost, but may be shut down for long running tasks in favour of other cloud users. This rarely happens with Nuke.',
    }

def build(submitter):
    """Build knobs to specify instance type."""
    knob = nuke.CascadingEnumeration_Knob(
        "cio_insttype",
        "Instance type", [k.NOT_CONNECTED])

    knob.setTooltip(TOOLTIPS["cio_insttype"])
    knob.setFlag(nuke.STARTLINE)

    submitter.addKnob(knob)

    knob = nuke.Boolean_Knob("cio_preemptible", "Preemptible")
    knob.setTooltip(TOOLTIPS["cio_preemptible"])
    submitter.addKnob(knob)
    knob.setValue(1)


def _sorter(inst_type):
    graphics = 1 if inst_type.get("gpu") else 0
    cores = inst_type["cores"]
    memory = float(inst_type["memory"])
    try:
        gpucores =  inst_type["total_gpu_cuda_cores"]
    except:
        gpucores = 0

    try:
        gpumemory =  float(inst_type["total_gpu_memory"])
    except:
        gpumemory = 0

    return "{}|{:04d}|{:06.2f}|{:07d}|{:06.2f}".format(graphics,cores,memory,gpucores,gpumemory)


def rebuild_menu(submitter, instance_types):
    """
    Repopulate the dropdown menu.

    Args:
        submitter (the submitter node)
        instance_types (list(dict)): new instance types
    """
    data = [it for it in instance_types or [] if it.get("operating_system", "linux") == "linux"]
    data.sort(key=_sorter)
    items = []
    for it in data:
        desc = it["description"]
        category = "GPU" if it.get("gpu") else "CPU"
        items.append("{}/{}".format(category,desc))
    submitter.knob("cio_insttype").setValues(items or [k.NOT_CONNECTED])

def resolve(submitter, **kwargs):
    instance_type = k.INVALID
    if coredata.valid():
        desc = submitter.knob("cio_insttype").value().split("/")[-1]
        instance_type = next((it["name"] for it in coredata.data()["instance_types"] if it["description"] == desc), k.INVALID)

    return {
        "instance_type":instance_type,
        "preemptible": bool(submitter.knob("cio_preemptible").getValue()) 
    }

def affector_knobs():
    return [
        "cio_insttype",
        "cio_preemptible"
    ]
