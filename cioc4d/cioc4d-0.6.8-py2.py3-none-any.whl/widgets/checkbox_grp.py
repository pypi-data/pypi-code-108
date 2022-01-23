

import c4d
from cioc4d.widgets import utils as wutil


class CheckboxGrp(object):
    """A group containing a label and checkbox"""

    def __init__(self, dialog, label ):
        self.label = label
        self.dialog = dialog
        self.checkbox_id = None
        self._build()
 
    def _build(self):
        with wutil.grid_group(self.dialog, cols=2):
            wutil.dotted_label(self.dialog, self.label)
            self.checkbox_id = self.dialog.register()
            self.dialog.AddCheckbox(
                    self.checkbox_id, c4d.BFH_SCALEFIT , initw=0, inith=0 , name="")

    def get_value(self):
        return self.dialog.GetBool(self.checkbox_id) 

    def set_value(self, value):
        self.dialog.SetBool(self.checkbox_id, value) 

