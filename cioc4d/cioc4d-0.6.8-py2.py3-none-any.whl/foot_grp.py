
from contextlib import contextmanager

import c4d


@contextmanager
def footer_group(dialog, **kwargs):
    grp_id = dialog.register()
    grp = dialog.GroupBegin(
        id=grp_id,
        flags=c4d.BFH_CENTER | c4d.BFV_BOTTOM,
        title="",
        rows=1,
        cols=kwargs.get("cols", 2),
        groupflags=0)
    if grp:
        dialog.GroupBorderSpace(5, 5, 5, 5)
        yield grp_id
    dialog.GroupEnd()


class FootGroup(object):

    def __init__(self, dialog):
        self.group_id = None
        self.dialog = dialog
        self.connect_button_id = None
        self.reset_button_id = None
        self.validate_button_id = None
        self.submit_button_id = None
        self._build()

    def _build(self):
        with footer_group(self.dialog, cols=4) as group_id:
            self.group_id = group_id
            self.connect_button_id = self.dialog.register()
            self.submit_button_id = self.dialog.register()
            self.validate_button_id = self.dialog.register()
            self.reset_button_id = self.dialog.register()

            self.dialog.AddButton(self.connect_button_id,
                                  c4d.BFV_CENTER,  name="Connect")
            self.dialog.AddButton(self.reset_button_id,
                                  c4d.BFV_CENTER,  name="Reset UI")
            self.dialog.AddButton(self.validate_button_id,
                                  c4d.BFV_CENTER,  name="Validate")
            self.dialog.AddButton(self.submit_button_id,
                                  c4d.BFV_CENTER,   name="Submit")
            self.enable_submit(False)
    def enable_submit(self, enable):
        self.dialog.Enable(self.submit_button_id, enable)
 