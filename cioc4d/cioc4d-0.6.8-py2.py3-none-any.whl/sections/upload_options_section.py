 
import c4d

from cioc4d.widgets.checkbox_grp import CheckboxGrp
from cioc4d.sections.collapsible_section import CollapsibleSection


class UploadOptionsSection(CollapsibleSection):

    ORDER = 80

    def __init__(self, dialog):
        self.use_daemon_widget = None

        super(UploadOptionsSection, self).__init__(
            dialog, "Upload Options", collapse=True)

    def build(self):
        self.use_daemon_widget = CheckboxGrp(self.dialog, "Use Upload Daemon")

    def populate_from_store(self):
        store = self.dialog.store
        self.use_daemon_widget.set_value(store.use_upload_daemon())

    def save_to_store(self):
        store = self.dialog.store
        store.set_use_upload_daemon(self.use_daemon_widget.get_value() )
        store.commit()


    def on_plugin_message(self, widget_id, msg):
        if widget_id in self._store_affectors:
            self.save_to_store()
            
    def resolve(self, expander, **kwargs):
        return {
            "local_upload": not self.use_daemon_widget.get_value()
        }
 
    def get_preview_affectors(self):
        return [
            self.use_daemon_widget.checkbox_id
        ]
 