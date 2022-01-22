# -*- coding: utf-8 -*-

"""Inversable dictionary.
"""


class invdict(dict):
    """Inversable dict::

         >>> -invdict({'key': 'val'}) == {'val': 'key'}
    """
    def __neg__(self):
        res = {}
        for k, v in self.items():
            res[v] = k
        return res
