

import c4d

from cioc4d.widgets import utils as wutil


class TextAreaGrp(object):
    """A group containing a label, textfield, and optional checkbox.

    TODO: Consolidate with HidableTextField.
    """

    def __init__(self, dialog, **kwargs):
        self.height=kwargs.get("height", 80)
        self.dialog = dialog
        self.text_area_id = None

        self._build()

    def _build(self):

        with wutil.grid_group(self.dialog, cols=1):

            self.text_area_id = self.dialog.register()
            self.dialog.AddMultiLineEditText(
                self.text_area_id,  c4d.BFH_SCALEFIT | c4d.BFV_TOP, initw=0, inith=self.height, style=c4d.DR_MULTILINE_READONLY)

    def set_value(self, value):
        self.dialog.SetString(self.text_area_id, value)

    def get_value(self):
        return self.dialog.GetString(self.text_area_id).strip()
