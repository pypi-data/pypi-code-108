from json import dumps


class Cmd(dict):

    def __init__(self, cmd: str, data: dict = None):
        dict.__init__(self, cmd=cmd, data=data)

    def __repr__(self) -> str:
        return dumps(self)
