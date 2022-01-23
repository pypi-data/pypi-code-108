"""
Handle the UI for output:

"""

import pymel.core as pm
from ciomaya.lib.ae import AEcommon

import json

def create_ui(node_attr):
    """Build static UI."""
    with AEcommon.ae_template():
        pm.scrollField("outputScrollField", height=250, editable=False, wordWrap=False)
        populate_ui(node_attr)

def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""
    attr = pm.Attribute(node_attr)
    field = AEcommon.find_ui("outputScrollField", pm.setParent(q=True))
    _on_output_change(attr, field)
    pm.scriptJob(attributeChange=(
        attr, pm.Callback( _on_output_change, attr, field)), parent=field, replacePrevious=True)


def _on_output_change(attr, field):
    data = attr.get()
    text = "Not valid"
    if data:
        try:
            obj =  json.loads(data)
            text = json.dumps(obj, sort_keys=True, indent=4)
        except BaseException:
            pass
    pm.scrollField(field, edit=True, text=text)
 