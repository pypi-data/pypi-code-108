
from cioc4d.widgets.hidable_text_field_grp import HidableTextFieldGrp
from cioc4d.sections.collapsible_section import CollapsibleSection


class AutosaveSection(CollapsibleSection):

    ORDER = 100

    def __init__(self, dialog):
        self.widget = None
        super(AutosaveSection, self).__init__(
            dialog, "Autosave", collapse=True)

    def build(self):
        self.widget = HidableTextFieldGrp(
            self.dialog, "Autosave Filename", extra_checkbox_label="Cleanup")

    def populate_from_store(self):
        store = self.dialog.store
        self.widget.set_visible(store.use_autosave())
        self.widget.set_value(store.autosave_filename())
        self.widget.set_extra_check_value(store.autosave_cleanup())
        self._disable_on_use_daemon()

    def save_to_store(self):
        store = self.dialog.store
        store.set_use_autosave(self.widget.get_visible())
        store.set_autosave_filename(self.widget.get_value())
        store.set_autosave_cleanup(self.widget.get_extra_check_value())
        store.commit()

    def on_plugin_message(self, widget_id, msg):
        if widget_id == self.widget.checkbox_id:
            self.widget.set_visible()
        elif widget_id == self.dialog.section("UploadOptionsSection").use_daemon_widget.checkbox_id:
            self._disable_on_use_daemon()

        if widget_id in self._store_affectors:
            self.save_to_store()

    def _disable_on_use_daemon(self):
        use_daemon = self.dialog.section(
            "UploadOptionsSection").use_daemon_widget.get_value()
        self.widget.set_extra_check_enabled(not use_daemon)

    def set_store_affectors(self):
        self._store_affectors = [
            self.widget.checkbox_id,
            self.widget.text_field_id,
            self.widget.extra_checkbox_id
        ]
