class SuperclassMeta(type):
    """
    Meta-class for superclasses.

    If a member of a subclass doesn't have a docstring, it copies the docstring of the corresponding member of
    the superclass.

    Source: https://stackoverflow.com/questions/40508492/python-sphinx-inherit-method-documentation-from-superclass.
    """

    def __new__(mcs, classname, bases, cls_dict):
        cls = super().__new__(mcs, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if not getattr(member, '__doc__'):
                try:
                    member.__doc__ = getattr(bases[-1], name).__doc__
                except (AttributeError, IndexError):
                    pass
        return cls
