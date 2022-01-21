from functools import partial

class semistaticmethod(object):
    def __init__(self, callable):
        self.f = callable
    def __get__(self, obj, type=None):
        if (obj is None) and (type is not None):
            return partial(self.f, type)
        if (obj is not None):
            return partial(self.f, obj)
        return self.f
    @property
    def __func__(self):
        return self.f