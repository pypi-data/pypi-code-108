
import c4d
import json
from cioc4d.widgets.int_field_grp import IntFieldGrp
from cioc4d.widgets.button_row import ButtonRow
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.text_area_grp import TextAreaGrp


class PreviewSection(CollapsibleSection):

    ORDER = 300

    def __init__(self, dialog):
        self.json_widget = None

        self.affectors = []

        super(PreviewSection, self).__init__(dialog, "Preview", collapse=True, override_color=c4d.Vector(0.2, 1,0.2))

    def build(self):
        self.actions_widget = ButtonRow(
            self.dialog, "Show Assets", button_width=120)
        self.json_widget = TextAreaGrp(self.dialog, height=200)

    def on_plugin_message(self, widget_id, msg):
        if widget_id in self.affectors:
            with_assets = widget_id == self.preview_button_id
            self.set_submission_preview(with_assets)

        if widget_id in self._store_affectors:
            self.save_to_store()

    def on_core_message(self, msg_id, msg):
        """Repopulate if EVMSG_CHANGE was emitted.

        It's possibly a result of the image paths being changed.
        """
        if msg_id in [c4d.EVMSG_CHANGE]:
            self.set_submission_preview(False)


    def set_submission_preview(self,  with_assets=False):
        submission = self.dialog.calculate_submission(with_assets=with_assets)
        self.json_widget.set_value(json.dumps(submission, indent=2))

    def set_affectors(self):
        """
        Get the IDs of widgets that can affect the preview
        """
        self.affectors = []
        self.affectors.append(self.dialog.foot_grp.connect_button_id)

        for section in self.dialog.sections:
            self.affectors += section.get_preview_affectors()

 


    def get_preview_affectors(self):
        """
        Collecting assets is potentially expensive as we need to hit the
        filesystem. For this reason, make the user click a button so they know
        what to expect.
        """
        return [
            self.actions_widget.button_ids[0]
        ]

    @property
    def preview_button_id(self):
        return self.actions_widget.button_ids[0]

