
import c4d

from cioc4d.widgets.int_field_grp import IntFieldGrp
from cioc4d.sections.collapsible_section import CollapsibleSection


class RetriesSection(CollapsibleSection):

    ORDER = 90

    def __init__(self, dialog):
        self.preempted_widget = None

        super(RetriesSection, self).__init__(
            dialog, "Automatic Retries", collapse=True)

    def build(self):
        self.preempted_widget = IntFieldGrp(
            self.dialog, "Retries When Preempted")

    def populate_from_store(self):
        store = self.dialog.store
        self.preempted_widget.set_value(store.retries_when_preempted())

    def save_to_store(self):
        store = self.dialog.store
        store.set_retries_when_preempted(self.preempted_widget.get_value())
        store.commit()

    def on_plugin_message(self, widget_id, msg):
        if widget_id in self._store_affectors:
            self.save_to_store()

    def resolve(self, expander, **kwargs):
        return {
            "autoretry_policy": {
                "failed": {
                    "max_retries": 0
                },
                "preempted": {
                    "max_retries": self.preempted_widget.get_value()
                }
            }
        }

    def get_preview_affectors(self):
        return [
            self.preempted_widget.int_field_id,
        ]
