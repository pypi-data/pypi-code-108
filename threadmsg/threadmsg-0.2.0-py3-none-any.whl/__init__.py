
import os
from . threadmsg import *

def loadConfig(fname):
    globals()["__info__"] = {}
    with open(fname) as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().replace("\t", " ").split(" ")
            k = parts.pop(0).strip()
            if '#' != k[0]:
                globals()["__%s__"%k] = " ".join(parts).strip()
                globals()["__info__"][k] = " ".join(parts).strip()

loadConfig(os.path.join(os.path.dirname(__file__), 'PROJECT.txt'))

