

class sdict(dict):
    """Sorted Dictionary class.
       Iterating over the sdict will give back the key/value pairs in
       order of insertion. A key can only be in a sdict once.
    """
    def __init__(self, **attrs):
        super(sdict, self).__init__()
        self._order = []
        for k, v in attrs.items():
            self[k] = v

    def __setitem__(self, key, val):
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)
        super(sdict, self).__setitem__(key, val)

    def __iter__(self):
        return ((key, self[key]) for key in self._order)

    def keys(self):
        return self._order

    def values(self):
        return [self[k] for k in self._order]
