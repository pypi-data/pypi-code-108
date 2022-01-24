class DictPrintingInOrderIgnoringNone(dict):
    """A dictionary that prints in the order of the keys, ignoring value None (or iterables containing only None).

    Examples
    --------
        >>> d = DictPrintingInOrderIgnoringNone({'b': 'x', 'a': 'y', 'c': 'z', 'd': 0, 'e': None, 'f': [None, None]})
        >>> print(d)
        {a: y, b: x, c: z, d: 0}
        >>> print(repr(d))
        {'a': 'y', 'b': 'x', 'c': 'z', 'd': 0}
    """

    def __repr__(self):
        return "{" + ", ".join([
            "%r: %r" % (key, self[key]) for key in sorted(self)
            if interesting_value(self[key])
        ]) + "}"

    def __str__(self):
        return "{" + ", ".join([
            "%s: %s" % (key, self[key]) for key in sorted(self)
            if interesting_value(self[key])
        ]) + "}"

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')


def interesting_value(value):
    if value is None:
        return False
    try:
        if all(element is None for element in value):
            return False
    except TypeError:
        return True
    return True
