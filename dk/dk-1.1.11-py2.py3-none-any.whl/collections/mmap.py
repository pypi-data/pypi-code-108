

class mmap(list):
    """Multi Map class, ie. a key/value collection where each key can
       occur multiple times. Implemented as a list of key/value tuples.
    """
    def __init__(self, **attrs):
        for k, v in attrs.items():
            self.add(k, v)

    def __repr__(self):
        vals = ', '.join('%s:%s' % kv for kv in self)
        return '<mmap: ' + vals + '>'

    __str__ = __repr__

    def add(self, key, val):
        super(mmap, self).append((key, val))

    def __iadd__(self, kv):
        key, val = kv
        self.add(key, val)

    def append(self, kv):
        key, val = kv
        self.add(key, val)

    def __setitem__(self, key, val):
        self.add(key, val)

    def __contains__(self, key):
        for k, v in self:
            if k == key:
                return True
        return False

    def __getitem__(self, key):
        for k, v in self:
            if key == k:
                yield v
