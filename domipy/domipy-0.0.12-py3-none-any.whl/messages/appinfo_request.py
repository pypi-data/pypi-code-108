"""
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import domipy


class AppInfoRequest(domipy.Command):
    """
        send: &APPINFO
    """
    def __init__(self):
        domipy.Command.__init__(self, "_APPINFO_", "_APPINFO_")

    def command(self):
        return "APPINFO"
