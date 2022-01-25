"""
The Extra assets widget.

The widget is a chunk of Qt embedded in Nuke's properties panel.
"""
import json
import nuke
from PySide2 import QtWidgets
from cionuke.components.conductor_knob import ConductorKnob
from ciopath.gpath_list import PathList
from cionuke import utils

NODE_BLACKLIST = ["Write", "DeepWrite"]

ASSETS_TOOLTIP = """
In the event tat some assets are not picked up by the dependency scraper, you may add them here.
To see what assets are found by the dependency scraper, go to the preview panel and press the show assets button. 
"""


class ExtraAssetsKnob(ConductorKnob):

    def __init__(self, submitter):
        """Set up the UI.

        UI consists of a Header row containing buttons, and list widget for the files.
        """

        super(ExtraAssetsKnob, self).__init__(submitter)

        self.button_layout = QtWidgets.QHBoxLayout()

        # Buttons
        for button in [
            {"label": "Clear", "func": self.clear},
            {"label": "Remove selected", "func": self.remove_selected},
            {"label": "Browse files", "func": self.browse_files},
            {"label": "Browse directory", "func": self.browse_dir},
        ]:

            btn = QtWidgets.QPushButton(button["label"])
            btn.setAutoDefault(False)
            btn.clicked.connect(button["func"])
            self.button_layout.addWidget(btn)

        self.content_layout.addLayout(self.button_layout)

        # List
        self.list_component = QtWidgets.QListWidget()
        self.list_component.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_component.setMaximumHeight(100)

        self.content_layout.addWidget(self.list_component)

    def updateValue(self):
        """
        Populate the UI from the hidden storage knob.

        Called automatically by Nuke when needed.
        """
        self.list_component.clear()
        try:
            assets = json.loads(self.submitter.knob(
                "cio_extra_assets").getText())
        except ValueError:
            assets = []
        self.list_component.addItems(assets)

    def entries(self):
        """Return the text of each entry."""
        result = []
        for i in range(self.list_component.count()):
            result.append(self.list_component.item(i).text())
        return result

    def on_edited(self):
        """
        Update the JSON in the hidden storage knob.
        """
        payload = json.dumps(self.entries())
        self.submitter.knob("cio_extra_assets").setValue(payload)

    def add_paths(self, *paths):
        """
        Add path items to the UI and update the stporage knob.

        Paths are deduplicated.
        """
        path_list = PathList(*self.entries())
        path_list.add(*paths)
        self.list_component.clear()
        self.list_component.addItems([p.fslash() for p in path_list])
        self.on_edited()

    def clear(self):
        """Clear the UI and update the storage knob."""
        self.list_component.clear()
        self.on_edited()

    def remove_selected(self):
        """Remove selected items and update the storage knob."""
        model = self.list_component.model()
        for row in sorted([index.row() for index in self.list_component.selectionModel().selectedIndexes()], reverse=True):
            model.removeRow(row)
        self.on_edited()

    def browse_files(self):
        """Browse for files to add."""
        result = QtWidgets.QFileDialog.getOpenFileNames(
            parent=None, caption="Select files to upload")
        if len(result) and len(result[0]):
            self.add_paths(*result[0])

    def browse_dir(self):
        """Browse for a folder to add."""
        result = QtWidgets.QFileDialog.getExistingDirectory(
            parent=None, caption="Select a directory to upload")
        if result:
            self.add_paths(result)


def build(submitter):
    """
    Build custom UI knob and a string knob for storage.

    The storage knob contains JSON.
    """
    cmd = "assets.ExtraAssetsKnob(nuke.thisNode())"

    knob = nuke.String_Knob("cio_extra_assets", "Extra Assets Raw", "")
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.PyCustom_Knob(
        "cio_extra_assets_ui", "Extra Assets",  cmd)
    knob.setFlag(nuke.STARTLINE)
    knob.setTooltip(ASSETS_TOOLTIP)
    submitter.addKnob(knob)

    knob = nuke.String_Knob("cio_pathmap", "Pathmap args")
    submitter.addKnob(knob)
    knob.setVisible(False)

def resolve(submitter, **kwargs):
    """
    Resolve the part of the payload that is handled by this component.
    """

    should_scrape_assets = kwargs.get("should_scrape_assets")
    extra_assets = json.loads(submitter.knob("cio_extra_assets").getText() or "[]")

    scraped_assets = scrape_assets(submitter) if should_scrape_assets else []
    path_list = PathList()
    path_list.add(*extra_assets)
    path_list.add(*scraped_assets)
    script  = nuke.Root().knob("name").getValue().strip()
    if not script:
        nuke.alert("No script name in Project Settings! Has this script been saved?")
    else:
        path_list.add(script)

    set_pathmap_args(submitter, path_list)

    path_list.remove_missing()
    path_list.glob()
    return {"upload_paths": sorted([p.fslash() for p in path_list])}

def set_pathmap_args(submitter, path_list):
    """Set up a drive letter remapping string for Windows."""
    prefix_set = set()

    for p in path_list:
        drive_letter = p.drive_letter
        if drive_letter.endswith(":"):
            prefix_set.add(p.drive_letter)
    mapping = []
    for p in prefix_set:
        mapping.append("{}/".format(p))
        mapping.append("/")

    submitter.knob("cio_pathmap").setValue( "{}".format(",".join(mapping)))

def scrape_assets(submitter):
    node_names=set()
    get_node_dependencies(submitter.fullName(), node_names)
    paths = set()
    for node_name in node_names:
        node = nuke.toNode(node_name)
        if node.Class() in NODE_BLACKLIST:
            continue
        knobs = [k for k in node.allKnobs() if k.Class() == "File_Knob"]
        for knob in knobs:
            value = utils.as_globbable_path(knob)
            if value:
                paths.add(value)
    return paths

def get_node_dependencies(node_name, visited=set()):
    """
    Collect nodes by name.
    """
    visited.add(node_name)
    node = nuke.toNode(node_name)
    node_names = set(filter(None,[_full_node_name(n) for n in node.dependencies()]))
    if node.Class() in ["Group", "LiveGroup"]:
        node_names |= set(filter(None,[_full_node_name(n) for n in node.nodes()]))
    for node_name in node_names:
        if node_name not in visited: # prevent loop
            get_node_dependencies(node_name, visited)


 
def _full_node_name(rhs):
    # Unexpectedly, either node.dependencies() or node.nodes() produces something
    # that might not be a node. It might be a knob. The example was
    # despillToColor2.falloff, so presumably it could have been:
    # grp1.grp2.node.parent_attr.child_attr 
    # We want the full node if it exists, so we rpartition in a loop to strip the attrs, and test
    # until we find it.
    name  = rhs.fullName()
    while 1:
        if not name:
            return None
        node =  nuke.toNode(name)
        if node:
            return name
        name = name.rpartition(".")[0]

def affector_knobs():
    """The hidden attribute us updated when the pyside ui changes, so we register that as the affector."""
    return [
        "cio_extra_assets"
    ]