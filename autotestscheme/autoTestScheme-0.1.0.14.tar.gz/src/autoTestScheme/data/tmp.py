

class Tmp(object):
    __species = None

    def __new__(cls, *args, **kwargs):
        if not cls.__species:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self):
        self.tmp = {}
        self.lastTmp = {}

    def append(self, key, value):
        self.tmp[key] = value

    def append_lastTmp(self, key, value):
        self.lastTmp[key] = value

    def get_lastTmp(self, key):
        if key not in list(self.lastTmp.keys()):
            return
        return self.lastTmp[key]

    def get(self, key):
        if key not in list(self.tmp.keys()):
            return
        return self.tmp.get(key)

tmp = Tmp()
