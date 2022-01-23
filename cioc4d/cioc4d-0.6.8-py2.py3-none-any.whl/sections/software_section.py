
# import os
from ciocore import data as coredata

from cioc4d.widgets.combo_box_grp import ComboBoxGrp
from cioc4d.sections.collapsible_section import CollapsibleSection
from ciocore.package_environment import PackageEnvironment


class SoftwareSection(CollapsibleSection):

    ORDER = 20

    def __init__(self, dialog):
        self.host_version_widget = None
        self.renderer_widget = None
        super(SoftwareSection, self).__init__(
            dialog, "Software", collapse=False)

    def build(self):
        self.host_version_widget = ComboBoxGrp(
            self.dialog, label="Cinema 4D Version")
        self.renderer_widget = ComboBoxGrp(self.dialog, label="Renderer")

    def populate_from_store(self):
        self.update_combo_items()

    def save_to_store(self):
        store = self.dialog.store
        store.set_host_version(self.host_version_widget.get_selected_value())
        store.set_renderer_version(self.renderer_widget.get_selected_value())
        store.commit()


    def on_plugin_message(self, widget_id, msg):

        if widget_id == self.dialog.foot_grp.connect_button_id:
            self.update_combo_items()
        elif widget_id == self.host_version_widget.combo_box_id:
            self.update_renderers_combo_items()
        
        if widget_id in self._store_affectors:
            self.save_to_store()

    def update_combo_items(self):
        self.host_version_widget.set_items(["-- Not Connected --"])
        self.renderer_widget.set_items(["-- Not Connected --"])
        if coredata.valid():
            store = self.dialog.store
            software_data = coredata.data()["software"]
            host_names = software_data.supported_host_names()
            if not host_names:
                return
            self.host_version_widget.set_items(
                host_names, default_value=store.host_version())
            self.update_renderers_combo_items()

    def update_renderers_combo_items(self):
        host = self.host_version_widget.get_selected_value()
        software_data = coredata.data()["software"]
        store = self.dialog.store

 
        renderers = software_data.supported_plugins(host)
        if not renderers:
            self.renderer_widget.set_items(["-- Default Renderer --"])
            return
        renderer_names = ["-- Default Renderer --"]
        for renderer in renderers:
            for version in renderer["versions"]:
                renderer_names.append("{} {}".format(
                    renderer["plugin"], version))
        self.renderer_widget.set_items(
            renderer_names, default_value=store.renderer_version())

    def resolve(self, expander, **kwargs):
        extra_env = self.dialog.section(
            "EnvironmentSection").get_entries(expander)

        packages_data = self.get_packages()
        if not packages_data:
            return {"software_package_ids": "INVALID"}

        packages_data["env"].extend(extra_env)
        return {
            "environment": dict(packages_data["env"]),
            "software_package_ids": packages_data["ids"]
        }

    def get_packages(self):
        if not coredata.valid():
            return
        tree_data = coredata.data()["software"]
        paths = []
        host_path = self.host_version_widget.get_selected_value()
        renderer_path = "{}/{}".format(host_path,
                                       self.renderer_widget.get_selected_value())
        paths = [host_path, renderer_path]

        result = {
            "ids": [],
            "env": PackageEnvironment()
        }
        for package in [_f for _f in [tree_data.find_by_path(path) for path in paths if path] if _f]:
            result["ids"].append(package["package_id"])
            result["env"].extend(package)

        return result

    def get_preview_affectors(self):
        return [
            self.host_version_widget.combo_box_id,
            self.renderer_widget.combo_box_id
        ]
