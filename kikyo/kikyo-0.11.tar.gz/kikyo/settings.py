import copy


class Settings(dict):
    def __init__(self, __values=None, **kwargs):
        super().__init__()
        self.update(__values, **kwargs)

    def __getitem__(self, name):
        return self.get(name)

    def deep(self, prefix) -> 'Settings':
        s = prefix.split('.')
        obj = self
        for i in s:
            if isinstance(obj, dict):
                if i in obj:
                    obj = obj[i]
                else:
                    obj = None
            else:
                obj = None
            if obj is None:
                break
        if obj is None:
            return Settings()
        return obj

    def get(self, name, default=None):
        return super().get(name, default)

    def getbool(self, name, default=None):
        v = self.get(name, default)
        return getbool(v)

    def getint(self, name, default=None):
        v = self.get(name, default)
        return getint(v)

    def getfloat(self, name, default=None):
        v = self.get(name, default)
        return getfloat(v)

    def getlist(self, name, default=None):
        v = self.get(name, default)
        return getlist(v)

    def set(self, name, value):
        self[name] = value

    def setdefault(self, k, default=None):
        if k not in self:
            self[k] = default

    def update(self, __values=None, **kwargs):
        if __values is not None:
            for name in __values:
                if isinstance(__values[name], dict):
                    self[name] = Settings(__values[name])
                else:
                    self[name] = __values[name]
        for k, v in kwargs.items():
            self[k] = Settings(v) if isinstance(v, dict) else v

    def merge(self, __values=None):
        if __values is not None:
            for name in __values:
                if isinstance(__values[name], dict):
                    v = Settings(__values[name])
                else:
                    v = __values[name]

                if name not in self:
                    self[name] = v
                else:
                    if isinstance(self[name], Settings) and isinstance(v, dict):
                        self[name].merge(v)
                    else:
                        self[name] = v

    def delete(self, name):
        del self[name]

    def copy(self):
        return copy.deepcopy(self)


def getbool(v):
    try:
        return bool(int(v))
    except (ValueError, TypeError):
        if v in ("True", "true"):
            return True
        if v in ("False", "false"):
            return False
    return None


def getint(v):
    try:
        return int(v)
    except (ValueError, TypeError):
        pass
    return None


def getfloat(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        pass
    return None


def getlist(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.split(",")
    elif not hasattr(v, "__iter__"):
        v = [v]
    return list(v)
