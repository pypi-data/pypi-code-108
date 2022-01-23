

import c4d
from cioc4d.widgets import utils as wutil


class ButtonRow(object):
    """A group containing any number of buttons in a row."""

    def __init__(self, dialog, *labels, **kwargs):
        self.label =  kwargs.get("label", "")
        self.dialog = dialog
        self.labels = labels
        self.button_ids = []
        self.num_buttons = len(labels)
        self._build(**kwargs)

    def _build(self, **kwargs):
        button_width = kwargs.get("button_width")
        with wutil.grid_group(self.dialog, cols=2):
            wutil.dotted_label(self.dialog, self.label)
            with wutil.grid_group(self.dialog, cols=self.num_buttons):
                for label in self.labels:
                    this_id = self.dialog.register()
                    self.button_ids.append(this_id)
                    if button_width:
                        self.dialog.AddButton(
                            this_id, c4d.BFH_FIT, initw=button_width,  name=label)
                    else:
                        self.dialog.AddButton(
                            this_id, c4d.BFH_SCALEFIT,  name=label)
