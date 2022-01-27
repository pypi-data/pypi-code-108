"""
:author: Zilvinas Binisevicius <zilvinas@binis.me>
"""
import domipy


class Ping(domipy.Command):
    """
        send: &PING message
    """
    def __init__(self):
        domipy.Command.__init__(self)

    def command(self):
        return "PING"
