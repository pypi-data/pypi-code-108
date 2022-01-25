from cytoolz.curried import curry, dissoc
from . import Sink
import os

try:
    import ujson as json
except ImportError:
    import json


FILE_PATH = "/Users/ian/work/m2gen/markers/Fusion/"


@curry
class TempAlterationSink(Sink):
    def __init__(self, filename):
        # todo: disregarding the filename
        pass

    def close(self):
        pass

    def write(self, unit):
        file_path = unit.get("file_path")
        rna_id = os.path.basename(file_path).split("_")[0]
        f = open(os.path.join(FILE_PATH, f"{rna_id}_fusion.jsonl"), "a")

        unit = dissoc(unit, "__type__", "file_path")
        f.write(json.dumps(unit))
        f.write("\n")
        f.close()
