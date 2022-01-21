"""NanamiLang immutable dict polyfill"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


class ImDict(dict):
    """ImDict Polyfill"""
    def __hash__(self):
        """Override default __hash__ behavior"""
        return id(self)

    # Also, deepcopy does not love our ImDict :DDD

    @staticmethod
    def _immutable(*_, **__):
        """Prevent data mutation (immutable dict)"""
        raise TypeError('ImDict: mutation was prevented')

    __setitem__ = __delitem__ = \
        clear = update = \
        setdefault = pop = popitem = _immutable

    # Reference: https://www.python.org/dev/peps/pep-0351/
