import nuke
from ciocore import data as coredata
from cionuke import const as k


def build(submitter):
    """
    Build knobs to specify software configuration.

    Currently only Nuke version.
    """
    knob = nuke.Enumeration_Knob("cio_software", "Nuke version", [k.NOT_CONNECTED])
    knob.setTooltip("Choose a Nuke version.")
    knob.setFlag(nuke.STARTLINE)
    submitter.addKnob(knob)


def rebuild_menu(submitter, software_data):

    if not software_data:
        return

    items = sorted(software_data.supported_host_names())
    submitter.knob("cio_software").setValues(items or [k.NOT_CONNECTED])
    if items:
        submitter.knob("cio_software").setValue(items[-1])

def resolve(submitter, **kwargs):

    if (not coredata.valid()) or submitter.knob("cio_software").value() == k.NOT_CONNECTED:
        return {"software_package_ids": [k.INVALID]}
    tree_data = coredata.data()["software"]
    selected = submitter.knob("cio_software").value()
    package_ids = []
    package = tree_data.find_by_path(selected)
    if package:
        package_ids = [package["package_id"]]
    return {"software_package_ids": package_ids}


def affector_knobs():
    return ["cio_software"]
