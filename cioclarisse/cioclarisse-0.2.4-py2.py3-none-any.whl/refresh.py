"""
Module concerned with refreshing the datablock and the attribute editor.
"""

import ix
from cioclarisse import (
    software_ui,
    debug_ui,
    frames_ui,
    instances_ui,
    projects_ui,
)

from ciocore import data as coredata


def force_ae_refresh(node):
    """
    Trigger an attribute editor refresh.

    Args:
        node (ConductorJob): item whose attribute editor to refresh.
    """
    attr = node.get_attribute("instance_type")
    count = attr.get_preset_count()
    applied = attr.get_applied_preset_index()
    if count:
        last = count - 1
        preset = (attr.get_preset_label(last), attr.get_preset_value(last))
        attr.remove_preset(last)
        attr.add_preset(preset[0], preset[1])
        attr.set_long(applied)


def refresh(_, **kw):
    """
    Respond to connect button click, and others that may benefit from a refresh.

    Update UI for projects and instances from the data block.

    Args:
        (kw["force"]): If true, invalidate the datablock and fetch fresh from
        Conductor. We update all ConductorJob nodes. Also update the log level
        in the UI.
    """
    try:
        coredata.data(force=True)
    except BaseException as ex:

        ix.log_error(
            """
Can't get data from Conductor. Try the connect button again.
If that doesn't work, your credentials file may be corrupt.
Please delete it from here (~/.config/conductor/credentials) and try again.
            """
        )
        raise

    nodes = ix.api.OfObjectArray()
    ix.application.get_factory().get_all_objects("ConductorJob", nodes)
    for node in nodes:
        projects_ui.update(node)
        instances_ui.update(node)
        software_ui.update(node)
        frames_ui.update_frame_stats_message(node)
    debug_ui.refresh_log_level(nodes)
