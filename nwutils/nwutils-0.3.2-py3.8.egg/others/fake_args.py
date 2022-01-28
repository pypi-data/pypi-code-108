from typing import Dict

class FakeArgs:
    def __init__(self, Dict:Dict):
        self.Dict = Dict
        for key in Dict:
            setattr(self, key, Dict[key])

    def __str__(self):
        return "FakeArgs: {%s}" % ", ".join([("%s => %s" % (k, v)) for (k, v) in self.Dict.items()])