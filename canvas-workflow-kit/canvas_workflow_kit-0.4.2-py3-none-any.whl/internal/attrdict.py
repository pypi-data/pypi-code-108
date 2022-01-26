from functools import singledispatch
from .string import snakecase


class AttrDict(dict):
    """A dictionary with attribute-style access. It maps attribute access to
    the real dictionary.  """

    def __init__(self, init={}):
        dict.__init__(self, init)

    def __getstate__(self):
        return self.__dict__.items()

    def __setstate__(self, items):
        for key, val in items:
            self.__dict__[key] = val

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))

    def __setitem__(self, key, value):
        return super(AttrDict, self).__setitem__(key, value)

    def __getitem__(self, name):
        return super(AttrDict, self).__getitem__(name)

    def __delitem__(self, name):
        return super(AttrDict, self).__delitem__(name)

    def __dir__(self):
        """Replace dict autocomplete choices with dict keys"""
        return self.keys()

    __getattr__ = __getitem__
    __setattr__ = __setitem__


@singledispatch
def to_attr_dict(arg):
    """
    Recursively converts an object or list of objects to an attribute dict
    with snake case
    """
    return arg


@to_attr_dict.register
def _(arg: list):
    return [to_attr_dict(i) for i in arg]


@to_attr_dict.register
def _(arg: dict):
    return AttrDict({snakecase(k): to_attr_dict(v) for k, v in arg.items()})
