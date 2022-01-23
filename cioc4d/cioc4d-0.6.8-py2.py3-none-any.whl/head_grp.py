
from contextlib import contextmanager

import c4d


@contextmanager
def head_group(dialog):
    grp = dialog.GroupBegin(
        id=dialog.register(),
        flags=c4d.BFH_SCALEFIT,
        rows=1,
        cols=2,
        groupflags=0)
    if grp:
        yield
    dialog.GroupEnd()


class HeadGroup(object):

    def __init__(self, dialog):
        self.dialog = dialog
        self._build()

    def _build(self):
        with head_group(self.dialog):
            self.dialog.AddGadget(c4d.DIALOG_PIN, 0)
            self.dialog.AddStaticText(
                id=self.dialog.register(),
                initw=0,
                inith=0,
                borderstyle=0,
                flags=c4d.BFH_SCALEFIT)
