import domipy

class Hello(domipy.Command):
    """
        send: HELLO message
    """
    def __init__(self):
        domipy.Command.__init__(self)

    def command(self):
        return "HELLO"
