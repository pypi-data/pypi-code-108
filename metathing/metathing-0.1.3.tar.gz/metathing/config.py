import typing as t
from pdb import set_trace as stop

class Config(dict):
    def __init__(self, defaults: t.Optional[dict] = None) -> None:
        dict.__init__(self, defaults or {})

    def from_object(self, obj: object) -> None:
        for key in obj:
            self[key] = obj[key]