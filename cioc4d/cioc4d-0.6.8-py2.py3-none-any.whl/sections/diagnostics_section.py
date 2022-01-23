
import c4d

from cioc4d.widgets.checkbox_grp import CheckboxGrp
from cioc4d.sections.collapsible_section import CollapsibleSection


class DiagnosticsSection(CollapsibleSection):

    ORDER = 120

    def __init__(self, dialog):
        self.widget = None
        self.fixture_widget = None
        super(DiagnosticsSection, self).__init__(
            dialog, "Diagnostics", collapse=True)

    def build(self):
        self.widget = CheckboxGrp(self.dialog, "Show Tracebacks")
        self.fixture_widget = CheckboxGrp(self.dialog, "Use Fixtures")

    def populate_from_store(self):
        self.widget.set_value(self.dialog.store.show_tracebacks())
        self.fixture_widget.set_value(self.dialog.store.use_fixtures())

    def save_to_store(self):
        store = self.dialog.store
        store.set_show_tracebacks(self.widget.get_value())
        store.set_use_fixtures(self.fixture_widget.get_value())
        store.commit()

    def on_plugin_message(self, widget_id, msg):
        if widget_id in self._store_affectors:
            self.save_to_store()

    def set_store_affectors(self):
        self._store_affectors =  [
            self.widget.checkbox_id,
            self.fixture_widget.checkbox_id,
        ]

