from poisson_approval.utils.SuperclassMeta import SuperclassMeta


class DictPrintingInOrder(dict, metaclass=SuperclassMeta):
    """A dictionary that prints in the order of the keys.

    Examples
    --------
        >>> d = DictPrintingInOrder({'b': 'x', 'a': 'y', 'c': 'z'})
        >>> print(d)
        {a: y, b: x, c: z}
        >>> print(repr(d))
        {'a': 'y', 'b': 'x', 'c': 'z'}
    """

    def __repr__(self):
        return "{" + ", ".join([
             "%r: %r" % (key, self[key]) for key in sorted(self)
        ]) + "}"

    def __str__(self):
        return "{" + ", ".join([
             "%s: %s" % (key, self[key]) for key in sorted(self)
        ]) + "}"

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')
