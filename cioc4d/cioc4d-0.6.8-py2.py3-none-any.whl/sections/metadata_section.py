
import c4d
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.key_value_widget import KeyValueHeader, KeyValueWidget


class MetadataSection(CollapsibleSection):
    ORDER=70
    def __init__(self, dialog):
        self.list_grp_id = None
        self.widgets = []
        super(MetadataSection, self).__init__(
            dialog, "Metadata", collapse=True)

    def build(self):
        self.header_row = KeyValueHeader(self.dialog)

        self.list_grp_id = self.dialog.register()

        self.dialog.GroupBegin(
            id=self.list_grp_id,
            flags=c4d.BFH_SCALEFIT,
            title="",
            cols=1,
            groupflags=0)

        self.dialog.GroupEnd()  # main

    def populate_from_store(self):
        self._update_widgets(self.dialog.store.metadata())

    def save_to_store(self):
        store = self.dialog.store
        value_tuples = [widget.get_values() for widget in self.widgets ] 
        store.set_metadata(  [t for t in value_tuples if t[0].strip()]  )
        store.commit()

    def on_plugin_message(self, widget_id, msg):
        if widget_id == self.header_row.add_button_id:  # clear list
            self.add_entry()
        else :
            self.maybe_remove_entry(widget_id)
 
        if widget_id in self._store_affectors:
            self.save_to_store()

    def add_entry(self):
        values = [widget.get_values() for widget in self.widgets]
        values.append(("", ""))
        self._update_widgets(values)

    def maybe_remove_entry(self, widget_id):
        keep_widgets = [
            w for w in self.widgets if w.delete_btn_id != widget_id]
        if len(keep_widgets) < len(self.widgets):

            values = [widget.get_values() for widget in keep_widgets]
            self._update_widgets(values)
            return True
        return False

    def _update_widgets(self, values):
        self.widgets = []
        self.dialog.LayoutFlushGroup(self.list_grp_id)
        for value_tuple in values:
            self.widgets.append(
                KeyValueWidget(self.dialog, *value_tuple))
        self.dialog.LayoutChanged(self.list_grp_id)


    def resolve(self, expander, **kwargs):
        metadata = {}
        for widget in self.widgets:
            name, value = widget.get_values()
            metadata[name]=value
        return {"metadata": expander.evaluate(metadata) }
 
    def get_preview_affectors(self):
        result = []
        result.append(self.header_row.add_button_id)
        for widget in self.widgets:
            result += [widget.name_field_id, widget.value_field_id, widget.delete_btn_id]
        return result