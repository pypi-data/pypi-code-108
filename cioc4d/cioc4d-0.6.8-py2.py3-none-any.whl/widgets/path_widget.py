

# encoding: utf-8
import c4d
from cioc4d.widgets import utils as wutil


class PathWidget(object):
    """A widget containing a label and textfield with a delete btn.
    
    Inteded to appear in a list, such as extra uploads.
    """

    def __init__(self, dialog, path):

        self.dialog = dialog
        self.group_id = None
        self.delete_btn_id = None
        self.text_field_id = None

        self._build()
        self.set_value(path)

    def _build(self):

        with wutil.grid_group(self.dialog, cols=2) as group_id:
            self.group_id = group_id
            self.delete_btn_id = self.dialog.register()
            self.dialog.AddButton(self.delete_btn_id,
                                  c4d.BFH_FIT, initw=0, name='X')

            self.text_field_id = self.dialog.register()
            self.dialog.AddEditText(
                self.text_field_id, c4d.BFH_SCALEFIT | c4d.BFV_TOP)

    def set_value(self, value):
        self.dialog.SetString(self.text_field_id, value)

    def get_value(self):
        return self.dialog.GetString(self.text_field_id).strip()
