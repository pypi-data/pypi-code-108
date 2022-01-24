# -*- coding: UTF-8 -*-
# Copyright 2013-2021 by Rumma & Ko Ltd.
# License: GNU Affero General Public License v3 (see file COPYING for details)

""" Turns a list of items into an endless loop. Useful when generating demo
fixtures.

See examples in :doc:`/topics/utils`.

"""


class Cycler(object):
    """

    An iterator that loops over an iteration and starts back at the beginning
    when it reaches the end.

    TODO: replace this by :func:`itertools.cycle`.

    """

    def __init__(self, *args):
        """
        If there is exactly one argument, then this must be an iterable
        and will be used as the list of items to cycle on.
        If there is more than one positional argument, then these
        arguments themselves will be the list of items.
        """

        if len(args) == 0:
            self.items = []
        elif len(args) == 1:
            if args[0] is None:
                self.items = []
            else:
                self.items = list(args[0])
        else:
            self.items = args
        self.current = 0

    def pop(self):
        if len(self.items) == 0:
            return None
        item = self.items[self.current]
        self.current += 1
        if self.current >= len(self.items):
            self.current = 0
        if isinstance(item, Cycler):
            return item.pop()
        return item

    def __len__(self):
        return len(self.items)

    def reset(self):
        self.current = 0


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
