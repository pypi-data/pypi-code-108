from .internal.attrdict import AttrDict


def assign_meta(new_class, bases, meta):
    m = {}
    for base in bases:
        m.update({k: v for k, v in getattr(base, "_meta", {}).items()})

    m.update({k: v for k, v in getattr(meta, "__dict__", {}).items() if not k.startswith("__")})
    _meta = AttrDict(m)

    return _meta


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that updates a _meta dict declared on base classes.
    """
    def __new__(mcs, name, bases, attrs):

        # Pop the Meta class if exists
        meta = attrs.pop('Meta', None)

        # Value of abstract by default should be set to false.
        # It is never inherited.
        abstract = getattr(meta, 'abstract', False)

        new_class = super().__new__(mcs, name, bases, attrs)

        _meta = assign_meta(new_class, bases, meta)

        _meta.abstract = abstract

        new_class._meta = _meta

        return new_class
