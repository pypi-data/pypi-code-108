

import c4d
import cioc4d.const as k
from cioc4d.widgets import utils as wutil


class IntFieldGrp(object):
    """A label and int field."""

    def __init__(self, dialog, label):
        self.dialog = dialog
        self.label = label
        self.int_field_id = None

        self._build()

    def _build(self):

        with wutil.grid_group(self.dialog, cols=2):

            wutil.dotted_label(self.dialog, self.label)

            self.int_field_id = self.dialog.register()
            self.dialog.AddEditNumberArrows(
                self.int_field_id, c4d.BFH_LEFT | c4d.BFV_TOP, initw=k.INT_FIELD_WIDTH)

    def set_value(self, value):
        self.dialog.SetInt32(self.int_field_id, value)

    def get_value(self):
        return self.dialog.GetInt32(self.int_field_id)
