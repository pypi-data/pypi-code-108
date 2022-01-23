import c4d
import cioc4d.const as k
from contextlib import contextmanager


def dotted_label(dialog, label):
    """Label, correct width, with dotted filler."""
    elem_id = dialog.register()
    dialog.AddStaticText(
        id=elem_id,
        initw=k.LABEL_WIDTH,
        inith=k.LABEL_HEIGHT,
        name=label,
        borderstyle=c4d.BORDER_TEXT_DOTTED,
        flags=c4d.BFH_FIT | c4d.BFV_TOP,
    )
    return elem_id


@contextmanager
def grid_group(dialog, **kwargs):
    """Group to contain gadgets for one widget."""
    grp_id = dialog.register()
    grp = dialog.GroupBegin(
        id=grp_id, flags=c4d.BFH_SCALEFIT, cols=kwargs.get("cols", 2), groupflags=0
    )
    if grp:
        yield grp_id
    dialog.GroupEnd()
