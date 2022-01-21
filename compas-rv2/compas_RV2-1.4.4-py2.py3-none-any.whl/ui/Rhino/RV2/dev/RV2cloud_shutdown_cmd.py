from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.ui import CommandMenu
from compas_rv2.rhino import get_proxy


__commandname__ = "RV2cloud_shutdown"


def RunCommand(is_interactive):

    config = {
        "name": "Cloud",
        "message": "Shutdown currently connect compas cloud server?",
        "options": [
            {
                "name": "Yes",
                "message": "Yes",
                "action": None
            },
            {
                "name": "No",
                "message": "No",
                "action": None
            }
        ]
    }

    menu = CommandMenu(config)
    action = menu.select_action()

    if action['name'] == 'Yes':
        p = get_proxy()
        p.shutdown()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
