

import c4d
# import cioc4d.const as k
from cioc4d.widgets import utils as wutil


class HidableTextFieldGrp(object):
    """A widget containing a label, a textfield, and checkbox to hide it.
    
    Also has an optional extra checkbox.
    """

    def __init__(self, dialog, label, **kwargs):
        self.dialog = dialog
        self.label = label
        self.helptext = kwargs.get("placeholder")
        self.group_id = None
        self.label_id = None
        self.checkbox_id = None
        self.text_field_id = None

        self.extra_checkbox_label = kwargs.get("extra_checkbox_label", None)
        self.extra_checkbox_id = None
        self.has_extra_checkbox = self.extra_checkbox_label != None
        self._build()

    def _build(self):

        cols = 4 if self.has_extra_checkbox else 3
        with wutil.grid_group(self.dialog, cols=cols) as group_id:
            self.group_id = group_id

            self.label_id = wutil.dotted_label(self.dialog, self.label)

            self.checkbox_id = self.dialog.register()
            self.dialog.AddCheckbox(
                id=self.checkbox_id, flags=c4d.BFH_LEFT, initw=30,  inith=0,   name="")

            self.text_field_id = self.dialog.register()
            self.dialog.AddEditText(
                self.text_field_id, c4d.BFH_SCALEFIT | c4d.BFV_TOP,
                editflags=c4d.EDITTEXT_HELPTEXT)

            if self.helptext:
                self.dialog.SetString(
                    self.text_field_id, self.helptext, flags=c4d.EDITTEXT_HELPTEXT)

            if self.has_extra_checkbox:
                self.extra_checkbox_id = self.dialog.register()
                self.dialog.AddCheckbox(
                    id=self.extra_checkbox_id, flags=c4d.BFH_RIGHT, initw=0,  inith=0, name=self.extra_checkbox_label)

        self.set_visible(True)

    def set_value(self, value):
        self.dialog.SetString(self.text_field_id, value)

    def get_value(self):
        return self.dialog.GetString(self.text_field_id).strip()

    def set_visible(self, value=None):
        if value != None:
            self.dialog.SetBool(self.checkbox_id, value)
        vis = self.dialog.GetBool(self.checkbox_id)
        self.dialog.HideElement(self.text_field_id, not vis)
        if self.has_extra_checkbox:
            self.dialog.HideElement(self.extra_checkbox_id, not vis)
        self.dialog.LayoutChanged(self.group_id)

    def get_visible(self):
        return self.dialog.GetBool(self.checkbox_id)

    def get_extra_check_value(self):
        if self.has_extra_checkbox:
            return self.dialog.GetBool(self.extra_checkbox_id)

    def set_extra_check_value(self, value):
        if self.has_extra_checkbox:
            return self.dialog.SetBool(self.extra_checkbox_id, value)

    def set_extra_check_enabled(self, enable):
        if self.has_extra_checkbox:
            self.dialog.Enable(self.extra_checkbox_id, enable)
            self.dialog.LayoutChanged(self.group_id)
