import c4d

from cioc4d.widgets.text_field_grp import TextFieldGrp
from cioc4d.sections.collapsible_section import CollapsibleSection


class LocationSection(CollapsibleSection):

    ORDER = 110

    def __init__(self, dialog):
        self.widget = None
        super(LocationSection, self).__init__(dialog, "Location", collapse=True)

    def build(self):
        self.widget = TextFieldGrp(self.dialog, label="Location Tag")

    def populate_from_store(self):
        self.widget.set_value(self.dialog.store.location_tag())

    def save_to_store(self):
        store = self.dialog.store
        store.set_location_tag(self.widget.get_value())
        store.commit()

    def on_plugin_message(self, widget_id, msg):
        if widget_id in self._store_affectors:
            self.save_to_store()

    def resolve(self, expander, **kwargs):
        location = self.widget.get_value()
        return {"location": location} if location else {}

    def get_preview_affectors(self):
        return [self.widget.text_field_id]
