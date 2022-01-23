# -*- coding: utf-8 -*-
import os

import c4d
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.combo_box_grp import ComboBoxGrp
from cioc4d.widgets.text_field_grp import TextFieldGrp
from cioc4d import utils
from ciocore import data as coredata

TAKE_OPTIONS = ["Current", "Marked", "Main"]


class GeneralSection(CollapsibleSection):

    ORDER = 10

    def __init__(self, dialog):
        self.takes_widget = None
        self.title_widget = None
        self.projects_widget = None
        self.destination_widget = None
        self.instance_types_widget = None

        super(GeneralSection, self).__init__(dialog, "General", collapse=False)

    def build(self):

        self.takes_widget = ComboBoxGrp(self.dialog, label="Takes")

        self.title_widget = TextFieldGrp(
            self.dialog, label="Job Title", placeholder="Title in Conductor dashboard"
        )

        self.projects_widget = ComboBoxGrp(self.dialog, label="Conductor Project")

        self.dialog.add_separator()

        self.instance_types_widget = ComboBoxGrp(
            self.dialog, label="Instance Type", checkbox=True, check_label="Preemptible"
        )

        self.dialog.Enable(self.takes_widget.combo_box_id, False)

    def populate_from_store(self):

        self.update_combo_items()

        store = self.dialog.store
        self.instance_types_widget.set_checkbox_value(store.preemptible())
        self.takes_widget.set_items(TAKE_OPTIONS)
        self.takes_widget.set_by_value(store.takes())
        self.title_widget.set_value(store.title())
        self.projects_widget.set_by_value(store.project())
        self.instance_types_widget.set_by_value(store.instance_type())

    def save_to_store(self):
        store = self.dialog.store
        store.set_preemptible(self.instance_types_widget.get_checkbox_value())
        store.set_takes(self.takes_widget.get_selected_value())
        store.set_title(self.title_widget.get_value())
        store.set_project(self.projects_widget.get_selected_value())
        store.set_instance_type(self.instance_types_widget.get_selected_value())
        store.commit()

    def on_plugin_message(self, widget_id, msg):
        if widget_id == self.dialog.foot_grp.connect_button_id:
            self.update_combo_items()

        if widget_id in self._store_affectors:
            self.save_to_store()

    def update_combo_items(self):
        if coredata.valid():
            store = self.dialog.store
            projects = coredata.data()["projects"]
            inst_types = coredata.data()["instance_types"]
            self.projects_widget.set_items(projects, default_value=store.project())
            self.instance_types_widget.set_items(
                [val["description"] for val in inst_types], default_value=store.instance_type()
            )
        else:
            self.projects_widget.set_items(["-- Not Connected --"])
            self.instance_types_widget.set_items(["-- Not Connected --"])

    def get_selected_instance_type(self):
        if not coredata.valid():
            return
        inst_types = coredata.data()["instance_types"]
        description = self.instance_types_widget.get_selected_value()
        return next((it for it in inst_types if it["description"] == description), None)

    def resolve(self, expander, **kwargs):
        instance_type = self.get_selected_instance_type()

        rpd = utils.rpd()
        try:
            resolved_title = c4d.modules.tokensystem.StringConvertTokens(
                self.title_widget.get_value(), rpd
            )
        except SystemError:
            resolved_title = "C4d untitled"

        return {
            "job_title": resolved_title,
            "project": self.projects_widget.get_selected_value(),
            "instance_type": instance_type["name"] if instance_type else "INVALID",
            "preemptible": self.instance_types_widget.get_checkbox_value(),
        }

    def get_preview_affectors(self):
        """See CollapsibleSection::get_preview_affectors"""
        return [
            self.takes_widget.combo_box_id,
            self.title_widget.text_field_id,
            self.projects_widget.combo_box_id,
            self.instance_types_widget.combo_box_id,
            self.instance_types_widget.checkbox_id,
        ]
