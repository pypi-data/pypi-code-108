# this is a marker for .pop(), otherwise we are not able to detect if a
# object is already in or not
_marker = object()

# Try to import the C-Extensions for AXTree
from ax.utils.ax_tree._ax_tree import _AXTree


def _build_axtree(_base_name, _base_parent_type):
    """
    Build a AXTree Class.
    Again it is possible to provide different base classes
    """

    # We need to override *all* methods from dict, otherwise
    # __getitem__, __setitem__ from _base_parent_type are NOT used.
    # They are responsible for breaking the 'dotted' keys into the tree.

    def __delitem__(self, key):
        parts = key.split('.')
        cur = self
        for n in parts[:-1]:
            cur = cur[n]
        _base_parent_type.__delitem__(cur, parts[-1])

    def number_of_leaves(self):
        return len(list(self.iter_leaf_keys()))

    def fromkeys(self, iterable, v=None):
        for key in iterable:
            self[key] = v

    def has_key(self, key):
        return key in self

    def pop(self, key, v=_marker):
        try:
            ret = self[key]
            del self[key]
            return ret
        except KeyError:
            if v is _marker:
                raise
            return v

    def setdefault(self, key, v=None):
        try:
            return self[key]
        except KeyError:
            self[key] = v
            return v

    def merge(self, tree):
        for key, value in tree.iter_leaf_items():
            if value == {} and self.has_key(key):
                continue
            self[key] = value

    # Zope RestrictedPython assumess structures (that are not dict or list) to
    # have __guarded_setitem__, __guarded_delitem__, __guarded_setattr__, and
    # __guarded_delattr__ attributes. For instance, classes not having these
    # attributes are not allowed to do assignments or del operations.
    # These statements will fail if the attributes are not included:
    #     x['5'] = 1
    #     del x['7']
    # Some background can be found in the RestrictedPython/Guards.py:103
    __guarded_setitem__ = _base_parent_type.__setitem__
    __guarded_delitem__ = _base_parent_type.__delitem__

    attributes = dict(locals())
    del attributes['_base_name']
    del attributes['_base_parent_type']
    return type(_base_name, (_base_parent_type,), attributes)


# Build an AXTree-Class where a 'plain' python dictionary is used for storage
AXTree = _build_axtree('AXTree', _AXTree)
