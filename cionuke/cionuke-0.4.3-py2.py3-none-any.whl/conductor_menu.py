"""
Build Conductor Menu.

This file is an extension of the user's ~/.nuke/menu.py
"""

try:
    from importlib import reload
except ImportError:
    from imp import reload
except ImportError:
    import reload

import nuke


from cionuke import const as k
from cionuke import const, entry, submit, validation, utils
from cionuke.components import (
    actions,
    advanced,
    autosave,
    conductor_knob,
    environment,
    assets,
    frames,
    instance_type,
    metadata,
    preview,
    project,
    software,
    title,
)
from cionuke.widgets import key_value_grp, notice_grp, buttoned_scroll_dialog


if k.FEATURE_DEV:

    reload(const)
    reload(utils)
    reload(notice_grp)
    reload(buttoned_scroll_dialog)
    reload(validation)
    reload(conductor_knob)
    reload(key_value_grp)
    reload(environment)
    reload(metadata)
    reload(assets)
    reload(frames)
    reload(project)
    reload(title)
    reload(actions)
    reload(instance_type)
    reload(software)
    reload(entry)
    reload(advanced)
    reload(preview)
    reload(autosave)
    reload(submit)


def dev_reload_recreate():
    """
    Dev mode reload

    Also removes Conductor node and creates a new one with all writes connected.
    """
    from cionuke import conductor_menu
    reload(conductor_menu)
    conductor_nodes = [n for n in nuke.allNodes("Group") if n.knob("cio_title")]
    for cn in conductor_nodes:
        nuke.delete(cn)

    for node in nuke.allNodes("Write"):
        node.setSelected(True)

    entry.add_to_nodes()
