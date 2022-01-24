"""QTile configuration submodule"""
from stonecharioteer.logger import logger, configure_logger


def config():
    """This function modifies the global variables, injecting
    parameters required to customize qtile."""
    configure_logger()
    logger.debug("Importing dependencies.")
    from libqtile.utils import guess_terminal

    logger.debug("Importing custom items")
    from stonecharioteer.qtile.groups import groups
    from stonecharioteer.qtile.inputs import MOD
    from stonecharioteer.qtile.layouts import layouts
    from stonecharioteer.qtile.screens import configure_screens
    from stonecharioteer.qtile.keymaps import configure_keymaps

    logger.debug("Building screens")
    configurables = {}
    screens = configure_screens()

    logger.debug("Setting `mod` key")
    configurables["mod"] = MOD.value
    logger.debug("Setting `groups`")
    configurables["groups"] = groups
    logger.debug("Setting `terminal`")
    configurables["terminal"] = guess_terminal()
    logger.debug("Setting `layouts`")
    configurables["layouts"] = layouts
    logger.debug("Setting `screens`")
    configurables["screens"] = screens
    logger.debug("Setting `keys`")
    configurables["keys"] = configure_keymaps(groups=groups)

    logger.debug("Setting misc. items.")
    # FIXME: Remove these later, or investigate if they're required.
    dgroups_key_binder = None
    configurables["dgroups_key_binder"] = dgroups_key_binder
    dgroups_app_rules = []  # type: List
    configurables["dgroups_app_rules"] = dgroups_app_rules
    follow_mouse_focus = True
    configurables["follow_mouse_focus"] = follow_mouse_focus
    bring_front_click = False
    configurables["bring_front_click"] = bring_front_click
    cursor_warp = False
    configurables["cursor_warp"] = cursor_warp
    auto_minimize = True
    configurables["auto_minimize"] = auto_minimize
    return configurables
