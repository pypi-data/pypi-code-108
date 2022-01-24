# Copyright 2015-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

'''This defines the :class:`Counter` class, a utility used in Jinja
templates to generate self-incrementing counters for sections,
subsections and any other sequences.

Usages and examples can be found in :doc:`/topics/utils`.

'''


class Counter(object):
    """Represents a counter. Usage see """
    def __init__(self, parent=None, start=0, step=1):
        self.children = []
        self.start = start
        self.step = step
        self.current = start
        self.named_items = dict()
        if parent is not None:
            parent.add_child(self)

    def add_child(self, ch):
        self.children.append(ch)

    def reset(self):
        self.current = self.start
        for ch in self.children:
            ch.reset()

    def __call__(self, name=None, value=None):
        if value is None:
            self.current += self.step
        else:
            self.current = value
        for ch in self.children:
            ch.reset()
        if name:
            if name in self.named_items:
                raise Exception("Cannot redefine name '{0}'.".format(name))
            self.named_items[name] = self.current
        return self.current

    def get(self, name):
        return self.named_items[name]()


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
