
import c4d
import re
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.hidable_text_field_grp import HidableTextFieldGrp


class NotificationSection(CollapsibleSection):
    ORDER = 75

    def __init__(self, dialog):
        self.widget = None

        super(NotificationSection, self).__init__(
            dialog, "Notifications", collapse=True)

    def build(self):

        self.widget = HidableTextFieldGrp(
            self.dialog, "Email Addresses")

    def populate_from_store(self):
        store = self.dialog.store
        self.widget.set_value(store.emails())
        self.widget.set_visible(store.use_emails())

    def save_to_store(self):
        store = self.dialog.store
        store.set_emails(self.widget.get_value())
        store.set_use_emails(self.widget.get_visible())
        store.commit()

    def on_plugin_message(self, widget_id, msg):
        if widget_id == self.widget.checkbox_id:
            self.widget.set_visible()
            
        if widget_id in self._store_affectors:
            self.save_to_store()

    def resolve(self, expander, **kwargs):
        if not self.widget.get_visible():
            return {}
        return {"notify": [a for a in re.split(r"[, ]+",  self.widget.get_value()) if a]}

    def get_preview_affectors(self):
        return [self.widget.text_field_id, self.widget.checkbox_id]
