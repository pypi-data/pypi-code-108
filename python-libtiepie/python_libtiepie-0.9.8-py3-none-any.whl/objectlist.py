class ObjectList(object):
    """"""

    def __init__(self):
        self._items = []

    def __getitem__(self, index):
        if index >= 0 and index < len(self._items):
            return self._items[index]
        else:
            raise IndexError()

    def __len__(self):
        return len(self._items)

    def _get_count(self):
        return len(self._items)

    count = property(_get_count)
