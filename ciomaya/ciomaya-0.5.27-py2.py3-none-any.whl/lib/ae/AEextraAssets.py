"""
Handle the UI for extra assets:
"""

import pymel.core as pm
 
from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI.
    """
 
    with AEcommon.ae_template():

        form = pm.formLayout(nd=100, height=200)
        clear_all_btn = pm.button("extraAssetsClearAllButton", label="Clear All", height=24)
        clear_sel_btn = pm.button("extraAssetsClearSelButton",label="Remove Selection", height=24)
        browse_file_btn = pm.button("extraAssetsBrowseFileButton",label="Browse Files", height=24)
        browse_dir_btn = pm.button("extraAssetsBrowseDirButton",label="Browse Folder", height=24)
        scroll_list = pm.textScrollList("extraAssetsScrollList",numberOfRows=10, allowMultiSelection=True)

        form.attachForm(clear_all_btn, "left", 2)
        form.attachPosition(clear_all_btn, "right", 2, 25)
        form.attachForm(clear_all_btn, "top", 2)
        form.attachNone(clear_all_btn, "bottom")

        form.attachPosition(clear_sel_btn, "left", 2, 25)
        form.attachPosition(clear_sel_btn, "right", 2, 50)
        form.attachForm(clear_sel_btn, "top", 2)
        form.attachNone(clear_sel_btn, "bottom")

        form.attachPosition(browse_file_btn, "left", 2, 50)
        form.attachPosition(browse_file_btn, "right", 2, 75)
        form.attachForm(browse_file_btn, "top", 2)
        form.attachNone(browse_file_btn, "bottom")

        form.attachPosition(browse_dir_btn, "left", 2, 75)
        form.attachForm(browse_dir_btn, "right", 2)
        form.attachForm(browse_dir_btn, "top", 2)
        form.attachNone(browse_dir_btn, "bottom")

        form.attachForm(scroll_list, "left", 2)
        form.attachForm(scroll_list, "right", 2)
        form.attachControl(scroll_list, "top", 2, clear_sel_btn)
        form.attachForm(scroll_list, "bottom", 2)

        pm.textScrollList(scroll_list, edit=True, append=("1", "2", "3"))

        pm.setParent("..")
     
    
        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""
    widgets = _get_widgets()
    attr = pm.Attribute(node_attr)

    pm.textScrollList(widgets["scroll_list"], edit=True, removeAll=True)
    paths = list(filter(None, [asset_attr.get() for asset_attr in pm.Attribute(node_attr)]))
    pm.textScrollList(widgets["scroll_list"], edit=True, append=paths)

    pm.button(
        widgets["clear_all_btn"],
        edit=True,
        command=pm.Callback(_on_clear_all_btn, attr)
    )
    pm.button(
        widgets["clear_sel_btn"],
        edit=True,
        command=pm.Callback(_on_clear_sel_btn, attr,  widgets["scroll_list"]),
    )
    pm.button(
        widgets["browse_file_btn"],
        edit=True,
        command=pm.Callback(_on_browse_btn, attr, 4),
    )
    pm.button(
        widgets["browse_dir_btn"],
        edit=True,
        command=pm.Callback(_on_browse_btn, attr, 3),
    )



def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    return {
        "clear_all_btn":  AEcommon.find_ui("extraAssetsClearAllButton", parent),
        "clear_sel_btn":  AEcommon.find_ui("extraAssetsClearSelButton", parent),
        "browse_file_btn":  AEcommon.find_ui("extraAssetsBrowseFileButton", parent),
        "browse_dir_btn":  AEcommon.find_ui("extraAssetsBrowseDirButton", parent),
        "scroll_list":  AEcommon.find_ui("extraAssetsScrollList", parent)
    }

 
def _on_clear_all_btn(attr):
    for element in attr:
        pm.removeMultiInstance(element, b=True)

def _on_clear_sel_btn(attr, scroll_list):
    sel_indices = [
        i - 1
        for i in pm.textScrollList(  scroll_list, q=True, selectIndexedItem=True
        )
    ]
    logical_indices = attr.getArrayIndices()
    for i in sel_indices:
        pm.removeMultiInstance(attr[logical_indices[i]], b=True)

def _on_browse_btn(attr, mode):
    caption = "Choose Files" if mode == 4 else "Choose Folder"

    entries = pm.fileDialog2(
        caption=caption,
        okCaption="Choose",
        fileFilter="*",
        dialogStyle=2,
        fileMode=mode,
        dir=pm.workspace.getPath(),
    )
    if entries:
        logical_indices = attr.getArrayIndices()
        next_index = logical_indices[-1] + 1 if logical_indices else 0
        for entry in entries:
            attr[next_index].set(entry)
            next_index += 1
        return
    pm.displayWarning("No files Selected")