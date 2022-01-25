from PySide2 import QtCore, QtWidgets
import re
import os
import shlex
from ciomax.sections.collapsible_section import CollapsibleSection
from ciomax.components.text_field_grp import TextFieldGrp
from ciomax.components.checkbox_grp import CheckboxGrp

from ciomax.components.int_field_grp import IntFieldGrp
from ciotemplate.expander import Expander
from ciopath.gpath import Path
import importlib


class AdvancedSection(CollapsibleSection):
    ORDER = 100

    def __init__(self, dialog):
        super(AdvancedSection, self).__init__(dialog, "Advanced")

        self.override_component =  CheckboxGrp(
            label="Override templates",
            checkboxes=1
        )
        self.content_layout.addWidget(self.override_component)

        self.script_component = TextFieldGrp(
            label="Pre submission script",
            placeholder="Python script"
        )
        self.content_layout.addWidget(self.script_component)

        self.task_template_component = TextFieldGrp(
            label="Task template",
            enablable=False)
        self.content_layout.addWidget(self.task_template_component)

        self.add_separator()

        self.retry_preempted_component = IntFieldGrp(
            label="Preempted retries", default=1, minimum=0, maximum=5)
        self.content_layout.addWidget(self.retry_preempted_component)

        self.notification_component = TextFieldGrp(
            label="Send Notifications",
            enablable=True)
        self.content_layout.addWidget(self.notification_component)

        self.location_component = TextFieldGrp(
            label="Location tag")
        self.content_layout.addWidget(self.location_component)

        upload_options_component = CheckboxGrp(
            label="Uploads",
            checkboxes=1,
            sublabels=["Use upload daemon"]
        )
        self.use_daemon_checkbox = upload_options_component.checkboxes[0]

        self.content_layout.addWidget(upload_options_component)

        self.add_separator()

        diagnostics_options_grp = CheckboxGrp(
            label="Developer",
            checkboxes=2,
            sublabels=["Show tracebacks", "Use fixtures"]
        )

        self.tracebacks_checkbox = diagnostics_options_grp.checkboxes[0]
        self.fixtures_checkbox = diagnostics_options_grp.checkboxes[1]
        self.content_layout.addWidget(diagnostics_options_grp)

        self.configure_signals()

    def configure_signals(self):
        """Write to store when values change."""

        self.task_template_component.field.editingFinished.connect(
            self.on_task_template_change)

        self.retry_preempted_component.field.valueChanged.connect(
            self.on_retry_preempted_change)

        self.notification_component.field.editingFinished.connect(
            self.on_notification_change)

        self.notification_component.display_checkbox.stateChanged.connect(
            self.on_use_notification_change)

        self.location_component.field.editingFinished.connect(
            self.on_location_change)

        # DAEMON
        self.use_daemon_checkbox.clicked.connect(
            self.on_use_daemon_change)

        self.tracebacks_checkbox.clicked.connect(
            self.on_show_tracebacks_change)

        self.fixtures_checkbox.clicked.connect(
            self.on_use_fixtures_change)

        self.override_component.checkboxes[0].clicked.connect(
            self.on_override_templates_change)

        self.script_component.field.editingFinished.connect(
            self.on_script_change)

    def on_task_template_change(self):
        self.dialog.store.set_task_template(
            self.task_template_component.field.text())

    def on_retry_preempted_change(self, value):
        self.dialog.store.set_retries_when_preempted(value)

    def on_notification_change(self):
        self.dialog.store.set_emails(self.notification_component.field.text())

    def on_use_notification_change(self, value):
        self.dialog.store.set_use_emails(value > 0)

    def on_location_change(self):
        self.dialog.store.set_location_tag(
            self.location_component.field.text())

    def on_use_daemon_change(self, value):
        self.dialog.store.set_use_upload_daemon(value > 0)

    def on_show_tracebacks_change(self, value):
        self.dialog.store.set_show_tracebacks(value > 0)

    def on_use_fixtures_change(self, value):
        use_fixtures = value > 0
        self.dialog.store.set_use_fixtures(use_fixtures)

    def on_override_templates_change(self, value):
        self.dialog.store.set_override_templates(value > 0)
        self.enable_templates()

    def on_script_change(self):
        self.dialog.store.set_script_filename(
            self.script_component.field.text())

    def run_presubmit_script(self, context, amendments_only=False):
        """
        Run a script according to the current render scope

        Args: 

            context (dict): tokens and their resolved values 

            amendments_only (bool, optional): fields to be amended to the payload. Defaults to False.

        Raises: ValueError: The command and args could not be interpreted by shlex

        Returns: dict: fields to be merged into the payload. See the resolve method of each section
            to understand how the various merges happen.
        """

        main_sequence = self.dialog.main_tab.section(
            "FramesSection").main_sequence
        context.update({
            "start": main_sequence.start,
            "end": main_sequence.end
        })
        expander = Expander(safe=True, **context)

        cmd = expander.evaluate(self.script_component.field.text())

        parts = shlex.split(cmd)
        if not parts:
            raise ValueError("Enter full path to script followed by args")

        script_path = Path(parts[0]).fslash()

        args = [self.dialog] + parts[1:]
 
        script_module = importlib.machinery.SourceFileLoader("", script_path).load_module() 
        if amendments_only:
            return script_module.amendments(*args)
        return script_module.main(*args)

    def enable_templates(self):
        enable = self.override_component.checkboxes[0].isChecked()
        self.script_component.setEnabled(enable)
        self.task_template_component.setEnabled(enable)

        self.on_renderer_change()


    def on_renderer_change(self):

        if not self.override_component.checkboxes[0].isChecked():
            software_section = self.dialog.main_tab.section("SoftwareSection")
            path = software_section.component.combobox.currentText()

            task_template = self.dialog.render_scope.get_task_template(path)
            script_template = self.dialog.render_scope.get_script_template(path)

            self.task_template_component.field.setText(task_template)
            self.script_component.field.setText(script_template)


    def populate_from_store(self):
        store = self.dialog.store
        super(AdvancedSection, self).populate_from_store(store)

        # First, set the checkbox state
        self.override_component.checkboxes[0].setChecked(store.override_templates())
        # Now populate templates withy whatever is in the store
        self.task_template_component.field.setText(store.task_template())
        self.script_component.field.setText(store.script_filename())
        # Now Enable/disable. If disable, on_renderer_change() will be called and fields will be
        # overwritten.
        self.enable_templates()


        # self.script_component.set_active(store.override_templates())

        self.retry_preempted_component.field.setValue(
            store.retries_when_preempted())

        self.notification_component.field.setText(store.emails())
        self.notification_component.set_active(store.use_emails())

        self.location_component.field.setText(store.location_tag())

        use_daemon = store.use_upload_daemon()
        self.use_daemon_checkbox.setChecked(use_daemon)

        self.tracebacks_checkbox.setChecked(store.show_tracebacks())
        self.fixtures_checkbox.setChecked(store.use_fixtures())

        return

    def resolve(self, expander, **kwargs):
        location = expander.evaluate(self.location_component.field.text())

        result = {}

        result["autoretry_policy"] = {
            "preempted": {
                "max_retries": self.retry_preempted_component.field.value()
            }
        }

        if self.notification_component.display_checkbox.isChecked():
            emails = list([_f for _f in re.split(
                r"[, ]+",  self.notification_component.field.text()) if _f])
            if emails:
                result["notify"] = emails

        if location:
            result["location"] = location

        result["local_upload"] = not self.use_daemon_checkbox.isChecked()

        return result
