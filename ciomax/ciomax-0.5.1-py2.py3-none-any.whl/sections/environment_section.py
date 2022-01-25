from PySide2 import QtWidgets, QtGui, QtCore
from ciocore import data as coredata
from ciomax.sections.collapsible_section import CollapsibleSection
from ciomax.components.key_value_grp import KeyValueGrpList
from ciocore.package_environment import PackageEnvironment

class EnvironmentSection(CollapsibleSection):
    ORDER = 60

    def __init__(self, dialog):
        super(EnvironmentSection, self).__init__(dialog, "Extra Environment")

        self.component = KeyValueGrpList(
            checkbox_label="Excl", key_label="Name")
        self.content_layout.addWidget(self.component)
        self.configure_signals()

    def configure_signals(self):
        """Write to store when values change"""
        self.component.edited.connect(self.on_edited)

    def on_edited(self):
        self.dialog.store.set_extra_environment(self.component.entries())

    def get_entries(self, expander):

        return [{
            "name": x[0],
            "value": expander.evaluate(x[1]),
            "merge_policy": "exclusive" if x[2] else "append"
        } for x in self.component.entries()]

    def populate_from_store(self):
        store = self.dialog.store
        super(EnvironmentSection, self).populate_from_store(store )
        
        self.component.set_entries(store.extra_environment())



    def resolve(self, expander, **kwargs):
        """
        Compose the environment submission sub-object.

        Consists of: 
            package = Environment provided by the package (Arnold / Vray etc.)
            CONDUCTOR_PATHHELPER = We currently handle all path remapping.
            self.get_entries() = stuff from this UI
            amendments = Stuff from presubmission script.
        """
        amendments = kwargs.get("amendments", {}).get("environment", [])

        if not coredata.valid():
            return {}
        software_section = self.dialog.main_tab.section("SoftwareSection")
        general_section = self.dialog.main_tab.section("GeneralSection")

        instance_type_name = general_section.instance_type_component.get_current_item_name()
        render_platform = "linux"
        if instance_type_name and instance_type_name.endswith("-w"):
            render_platform = "windows"

        tree_data = coredata.data()["software"]
        paths = software_section.get_all_software_paths()
        env = PackageEnvironment(render_platform=render_platform)
        for path in paths:
            package = tree_data.find_by_path(path)
            env.extend(package)

        env.extend(self.get_entries(expander))
        env.extend(amendments)

        return { "environment": dict(env)}



