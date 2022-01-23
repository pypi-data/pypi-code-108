

import c4d
from cioc4d.widgets import utils as wutil


class ComboBoxGrp(object):
    """
    A group containing a label, combobox, and optional checkbox
    
    Useful for instancetypes with a preemptible checkbox
    """

    def __init__(self, dialog, **kwargs):
        self.dialog = dialog
        self.has_checkbox = kwargs.get("checkbox")
        self.label = kwargs.get("label", "")
        self.check_label = kwargs.get("check_label", "")

        self.checkbox_id = None
        self.combo_box_id = None
        self.items = []

        self._build()

    def _build(self):
        cols = 3 if self.has_checkbox else 2
        with wutil.grid_group(self.dialog, cols=cols):
            self.combo_box_id = self.dialog.register()
            wutil.dotted_label(self.dialog, self.label)
            self.dialog.AddComboBox(self.combo_box_id, c4d.BFH_SCALEFIT)
            if self.has_checkbox:
                self.checkbox_id = self.dialog.register()
                self.dialog.AddCheckbox(
                    self.checkbox_id, c4d.BFH_RIGHT, 0, 0, self.check_label)

    def clear(self):
        self.dialog.FreeChildren(self.combo_box_id)

    def set_items(self, options, default_value=None):
        """
        Set the combobox to contain the given list of items.

        Strategy to set the selected item:
        1. Existing value if it exists in the list of new items.
        2. Default value if given
        3. First item in the list.

        If the calling function wants to set a different item, it must do so
        explicitly afterwards.
        """
        value = self.get_selected_value()
        if value and value.startswith("--"):
            value = default_value or None
        
        self.clear()
        self.items = []

        for option in options:
            item_id = self.dialog.register()
            self.dialog.AddChild(self.combo_box_id, item_id, option)
            self.items.append((item_id, option))
        
        if not (value and self.set_by_value(value)) :
            self.set_by_index(0)

    def set_by_id(self, item_id):
        self.dialog.SetInt32(self.combo_box_id, item_id)

    def set_by_index(self, index):
        if index < 0:
            index = len(self.items)+index
        self.set_by_id(self.items[index][0])

    def set_by_value(self, value):
        item = next((x for x in self.items if x[1] == value), None)
        if not item:
            return False
        self.set_by_id(item[0])
        return True

    def get_selected_value(self):
        selected_id = self.dialog.GetInt32(self.combo_box_id)
        item = next((x for x in self.items if x[0] == selected_id), None)
        if item:
            return item[1]

    def set_checkbox_value(self, value):
        self.dialog.SetBool(self.checkbox_id, value)

    def get_checkbox_value(self):
        return self.dialog.GetBool(self.checkbox_id)
