

import c4d
from cioc4d.widgets import utils as wutil


class TextGrp(object):
    """A group containing a label, and static text.
    
    TODO: Label should not be kwargs.
    """

    def __init__(self, dialog, **kwargs):
        self.dialog = dialog
        self.label = kwargs.get("label", "")
        self.text_id = None
        self._build()

    def _build(self):
        with wutil.grid_group(self.dialog, cols=2):
            wutil.dotted_label(self.dialog, self.label)

            self.text_id = self.dialog.register()
            self.dialog.AddStaticText(
                self.text_id,
                c4d.BFH_SCALEFIT | c4d.BFV_TOP)

    def set_value(self, value):
        self.dialog.SetString(self.text_id, value)

    def get_value(self):
        return self.dialog.GetString(self.text_id)
