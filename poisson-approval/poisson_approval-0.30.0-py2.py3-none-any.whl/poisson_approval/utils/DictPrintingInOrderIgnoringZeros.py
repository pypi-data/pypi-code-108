import numpy as np


class DictPrintingInOrderIgnoringZeros(dict):
    """A dictionary that prints in the order of the keys, ignoring values such as 0, None...

    Notes
    -----
    All values whose boolean conversion is False are ignored when converting to string: 0, None, [], all empty
    containers, etc. Empty `numpy` arrays are also ignored.

    Examples
    --------
        >>> d = DictPrintingInOrderIgnoringZeros({'b': 'x', 'a': 'y', 'c': 'z', 'd': 0, 'e': None, 'f': []})
        >>> print(d)
        {a: y, b: x, c: z}
        >>> print(repr(d))
        {'a': 'y', 'b': 'x', 'c': 'z'}
    """

    def __repr__(self):
        return "{" + ", ".join([
            "%r: %r" % (key, self[key]) for key in sorted(self)
            if (isinstance(self[key], np.ndarray) and len(self[key]) > 0) or (
                not isinstance(self[key], np.ndarray) and self[key])
        ]) + "}"

    def __str__(self):
        return "{" + ", ".join([
            "%s: %s" % (key, self[key]) for key in sorted(self)
            if (isinstance(self[key], np.ndarray) and len(self[key]) > 0) or (
                not isinstance(self[key], np.ndarray) and self[key])
        ]) + "}"

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')
