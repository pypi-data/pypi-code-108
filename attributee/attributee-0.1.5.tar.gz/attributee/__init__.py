
import inspect

from typing import Any, Optional, Type, Union

from collections import Mapping, OrderedDict

class AttributeException(Exception):
    pass

class AttributeParseException(AttributeException):
    def __init__(self, cause, key):
        self._keys = []
        if isinstance(cause, AttributeParseException):
            self._keys.extend(cause._keys)
            cause = cause.__cause__ or cause.__context__
        super().__init__(cause)
        self._keys.insert(0, key)
 
    def __str__(self):
        return "Attribute error: {}".format(".".join(self._keys))

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

class CoerceContext():

    def __init__(self, parent: Optional["Attributee"] = None, key: Optional[Any] = None) -> None:
        self._parent = parent
        self._key = key

    @property
    def parent(self) -> Optional["Attributee"]:
        return self._parent

    @property
    def key(self) -> Optional[Any]:
        return self._key

@singleton
class Undefined():
    pass

def is_undefined(a):
    if a is None:
        return False
    return a == Undefined()

def is_instance_or_subclass(val, class_) -> bool:
    """Return True if ``val`` is either a subclass or instance of ``class_``."""
    try:
        return issubclass(val, class_)
    except TypeError:
        return isinstance(val, class_)

class Attribute(object):

    def __init__(self, default=Undefined(), description=""):
        self._default = default if is_undefined(default) else (None if default is None else self.coerce(default, CoerceContext()))
        self._description = description

    def coerce(self, value, context: Optional[CoerceContext] = None):
        return value

    def dump(self, value):
        return value

    @property
    def default(self):
        return self._default

    @property
    def description(self):
        return self._description

    @property
    def required(self):
        return is_undefined(self._default)

class Any(Attribute):
    pass

class Nested(Attribute):

    def __init__(self, acls: Type["Attributee"], override: Mapping = None, create: bool = True, **kwargs):
        if not issubclass(acls, Attributee):
            raise AttributeException("Illegal base class {}".format(acls))

        self._acls = acls
        self._override = dict(override.items() if not override is None else [])
        self._create = create
        if "default" not in kwargs:
            self._required = False

            for _, afield in acls.list_attributes():
                if afield.required:
                    self._required = True
            if not self._required:
                kwargs["default"] = {}
        else:
            self._required = False

        super().__init__(**kwargs)

    def coerce(self, value, _):
        if value is None:
            return None
        assert isinstance(value, Mapping), "Only mapping accepted as an input"
        kwargs = dict(value.items())
        kwargs.update(self._override)
        if self._create:
            return self._acls(**kwargs)
        else:
            return kwargs

    def dump(self, value: Union["Attributee", Mapping]):
        if value is None:
            return None
        if self._create:
            return value.dump()
        else:
            return value

    def attributes(self):
        return self._acls.attributes()

    @property
    def required(self):
        return super().required and self._required

    def __getattr__(self, name):
        # This is only here to avoid pylint errors for the actual attribute field
        return super().__getattr__(name)

    def __setattr__(self, name, value):
        # This is only here to avoid pylint errors for the actual attribute field
        super().__setattr__(name, value)


class AttributeeMeta(type):

    @staticmethod
    def _get_fields(attrs: Mapping, pop=False):
        """Get fields from a class.
        :param attrs: Mapping of class attributes
        """
        fields = []
        for field_name, field_value in attrs.items():
            if is_instance_or_subclass(field_value, Attribute):
                fields.append((field_name, field_value))
        if pop:
            for field_name, _ in fields:
                del attrs[field_name]

        return fields

    # This function allows Schemas to inherit from non-Schema classes and ensures
    #   inheritance according to the MRO
    @staticmethod
    def _get_fields_by_mro(klass):
        """Collect fields from a class, following its method resolution order. The
        class itself is excluded from the search; only its parents are checked. Get
        fields from ``_declared_attributes`` if available, else use ``__dict__``.

        :param type klass: Class whose fields to retrieve
        """
        mro = inspect.getmro(klass)
        # Loop over mro in reverse to maintain correct order of fields
        return sum(
            (
                AttributeeMeta._get_fields(
                    getattr(base, "_declared_attributes", base.__dict__)
                )
                for base in mro[:0:-1]
            ),
            [],
        )

    @classmethod
    def __prepare__(self, name, bases):
        return OrderedDict()

    def __new__(mcs, name, bases, attrs):

        cls_attributes = AttributeeMeta._get_fields(attrs, pop=True)
        klass = super().__new__(mcs, name, bases, attrs)
        inherited_attributes = AttributeeMeta._get_fields_by_mro(klass)

        # Assign attributes on class
        klass._declared_attributes = OrderedDict(inherited_attributes + cls_attributes)

        return klass

class Collector(Attribute):

    def filter(self, object: "Attributee", **kwargs):
        return {}

class Include(Nested, Collector):

    def filter(self, object: "Attributee", **kwargs):
        attributes = self._acls.attributes()
        filtered = dict()
        for aname, afield in attributes.items():
            if isinstance(afield, Collector):
                filtered.update(afield.filter(object, **kwargs))
            elif aname in kwargs:
                filtered[aname] = kwargs[aname]
        return filtered

class Attributee(metaclass=AttributeeMeta):
    """Base class for all objects that utilize declarative initialization.

    """

    def __init__(self, *args, **kwargs):
        """Base constructor, should be called by sublasses. It is important that you pass all unhandled arguments to
        it to use the functionalities properly.

        Raises:
            AttributeException: [description]
            AttributeParseException: [description]
        """
        super().__init__()
        attributes = getattr(self.__class__, "_declared_attributes", {})

        unconsumed = set(kwargs.keys())
        unspecified = set(attributes.keys())

        for avalue, aname in zip(args, filter(lambda x: not isinstance(attributes[x], Collector) and x not in kwargs, attributes.keys())):
            if aname in kwargs:
                raise AttributeException("Argument defined as positional and keyword: {}".format(aname))
            kwargs[aname] = avalue

        for aname, afield in attributes.items():
            try:
                if isinstance(afield, Collector):
                    iargs = afield.filter(self, **kwargs)
                    super().__setattr__(aname, afield.coerce(iargs, CoerceContext(parent=self)))
                    unconsumed.difference_update(iargs.keys())
                    unspecified.difference_update(iargs.keys())
                else:
                    if not aname in kwargs:
                        if not afield.required:
                            avalue = afield.default
                            super().__setattr__(aname, avalue)
                        else:
                            continue
                    else:
                        avalue = kwargs[aname]
                        try:
                            value = afield.coerce(avalue, CoerceContext(parent=self))
                            super().__setattr__(aname, value)
                        except AttributeException as ae:
                            raise AttributeParseException(ae, aname) from ae
                        except AttributeError as ae:
                            raise AttributeParseException(ae, aname) from ae
            except AttributeError:
                raise AttributeException("Illegal attribute name {}, already taken".format(aname))
            unconsumed.difference_update([aname])
            unspecified.difference_update([aname])

        if unspecified:
            raise AttributeException("Missing arguments: {}".format(", ".join(unspecified)))

        if unconsumed:
            raise AttributeException("Unsupported arguments: {}".format(", ".join(unconsumed)))

    def __setattr__(self, key, value):
        attributes = getattr(self.__class__, "_declared_attributes", {})
        if key in attributes:
            raise AttributeException("Attribute {} is readonly".format(key))
        super().__setattr__(key, value)

    @classmethod
    def attributes(cls):
        from .containers import ReadonlyMapping
        attributes = getattr(cls, "_declared_attributes", {})
        return ReadonlyMapping(attributes)

    def dump(self, ignore=None):
        attributes = self.__class__.attributes()
        if attributes is None:
            return OrderedDict()
    
        serialized = OrderedDict()
        for aname, afield in attributes.items():
            if ignore is not None and aname in ignore:
                continue
            if isinstance(afield, Collector):
                serialized.update(afield.dump(getattr(self, aname, {})))
            else:
                serialized[aname] = afield.dump(getattr(self, aname, afield.default))
                
        return serialized

    @classmethod
    def list_attributes(cls):
        for name, attr in cls.attributes().items():
            yield (name, attr)

class Unclaimed(Collector):

    def __init__(self, description=""):
        super().__init__({}, description=description)

    def filter(self, object: "Attributee", **kwargs):
        attributes = object.attributes()
        claimed = set()
        for aname, afield in attributes.items():
            if isinstance(afield, Collector) and not isinstance(afield, Unclaimed):
                claimed.update(afield.filter(object, **kwargs).keys())
            elif aname in kwargs:
                claimed.add(aname)
        return {k: v for k, v in kwargs.items() if k not in claimed}

from attributee.primitives import Integer, Float, String, Boolean, Enumeration, Primitive, Number
from attributee.object import Object, Callable, Date, Datetime
from attributee.containers import List, Map, Tuple