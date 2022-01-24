"""This module contains monitor and display related functions
This early implementation of this module is copied from https://stackoverflow.com/a/64502961
"""
from Xlib import display
from Xlib.ext import randr


def find_mode(id, modes):
    """Returns a list of resolutions for a display mode"""
    for mode in modes:
        if id == mode.id:
            return "{}x{}".format(mode.width, mode.height)


def get_display_info():
    """Returns a list of dictionaries containing display name, the current
    resolution and available resolutions"""
    import os

    d = display.Display(os.environ.get("DISPLAY", ":0"))
    result = []
    screen = 0
    info = d.screen(screen)
    window = info.root

    res = randr.get_screen_resources(window)
    for output in res.outputs:
        params = d.xrandr_get_output_info(output, res.config_timestamp)
        if not params.crtc:
            continue
        crtc = d.xrandr_get_crtc_info(params.crtc, res.config_timestamp)
        modes = set()
        for mode in params.modes:
            modes.add(find_mode(mode, res.modes))
        result.append(
            {
                "name": params.name,
                "resolution": "{}x{}".format(crtc.width, crtc.height),
                "available_resolutions": list(modes),
            }
        )

    return result
