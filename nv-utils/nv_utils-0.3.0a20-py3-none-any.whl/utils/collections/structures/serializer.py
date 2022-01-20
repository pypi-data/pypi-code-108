"""
This is a 'quick & dirt' serializer that was built to parse xml and json files.  Please refer to other projects such
as attrs or cattrs, or even Marshmellow before considering this serializer. While there is no planned deprecation,
once their dependencies migrate to one of these projects, it shall be discontinued from here.

"""

import collections
import json
import logging
from importlib.util import find_spec

import datetime

from nv.utils.parsers.string import parse_date, parse_datetime
from nv.utils.decorators import requires

# Conditional imports
if find_spec('dicttoxml'):
    import dicttoxml
else:
    dicttoxml = None

if find_spec('xmltodict'):
    import xmltodict
else:
    xmltodict = None


logger = logging.getLogger(__name__)


__ALL__ = ['to_structure', 'from_structure', 'SerializerField', 'SerializerList', 'SerializerDate',
           'SerializerDateTime', 'SerializerMixin', 'SerializerStrictMixin', 'SerializerRootlessMixin', ]


def to_structure(obj, structure=None, strict=False, use_internal_names=False):
    structure = structure or dict()
    if isinstance(obj, SerializerMixin):
        return obj.as_structure(use_internal_names=use_internal_names)
    elif isinstance(obj, collections.Mapping):
        d = dict()
        for k, v in obj.items():
            field = structure.get(k, None if strict else SerializerField(k))
            if field is None:
                continue
            rootless = getattr(v, '_rootless', getattr(field.constructor, '_rootless', False))
            if rootless:
                d.update(v.as_structure(use_internal_names=use_internal_names))
            else:
                d[field.name if use_internal_names else field.interface] = to_structure(v, use_internal_names=use_internal_names)
        return d
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [to_structure(v, use_internal_names=use_internal_names) for v in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj.as_structure(use_internal_names=use_internal_names) if hasattr(obj, 'as_strutcture') else obj


def from_structure(cls, elmt):
    logger.debug(f'Parsing elements typed {type(elmt)}: {elmt!r}')
    blueprint = cls.get_blueprint()
    obj = cls.__new__(cls)
    for interface, field in blueprint.items():
        logger.debug(f'Looking for {field.name} ({field.constructor!r}) as {interface}')
        if getattr(field.constructor, '_rootless', False):
            params = dict()
            for k in field.constructor.get_blueprint():
                v = elmt.get(k, None)
                if v is not None:
                    params.update({k: v})
        else:
            params = elmt.get(interface, field.default)
        logger.debug(f"Params found: {params!r}")
        if params is None and not field.optional:
            msg = f"Field {field.name} is not optional when building {obj!r}"
            logger.error(msg)
            raise AttributeError(msg)
        setattr(obj, field.name, field.from_structure(params) if params is not None else None)
    return obj


class SerializerBase(object):
    @classmethod
    def from_structure(cls, elmt):
        return NotImplemented

    @classmethod
    def from_json(cls, j, *args, **kwargs):
        return cls.from_structure(json.loads(j, *args, **kwargs))

    def as_structure(self, use_internal_names=False):
        return NotImplemented

    def as_json(self, use_internal_names=False):
        return json.dumps(self.as_structure(use_internal_names=use_internal_names))


class SerializerField(SerializerBase):
    def __init__(self, interface, constructor=None, default=None, optional=True, name=None):
        self.interface = interface
        self.constructor = constructor or str
        self.name = name or interface
        self.default = default
        self.optional = optional

    def from_structure(self, elmt):
        logger.debug(f"Field {self.name} will parse {elmt!r}")
        if hasattr(self.constructor, 'from_structure'):
            return self.constructor.from_structure(elmt)
        return self.constructor(elmt)

    def __repr__(self):
        return f"SerializerField({self.interface!r}, name={self.name!r}, constructor={self.constructor!r}, " \
               f"default={self.default!r}, optional={self.optional!r})"


class SerializerList(SerializerField):
    def __init__(self, interface, constructor=None, *args, **kwargs):
        self.element_constructor = constructor.from_structure if hasattr(constructor, 'from_structure') else constructor
        super().__init__(interface, constructor=self._constructor, *args, **kwargs)

    def _constructor(self, elmts):
        logger.debug(f"List {self.name or self.interface} will parse {elmts!r}")

        # workaround for dicts made from XML lists and single item lists
        if isinstance(elmts, collections.Mapping):
            elmts = elmts.get('item', [elmts])

        if self.element_constructor is not None:
            return [self.element_constructor(elmt) for elmt in elmts]
        return elmts

    def __repr__(self):
        return f"SerializerList({self.interface!r}, constructor={self.element_constructor!r})"


class SerializerDate(SerializerField):
    def __init__(self, interface, constructor=None, default=None, optional=True, name=None):
        super().__init__(interface, constructor=constructor or self._constructor, default=default, optional=optional, name=name)

    def _constructor(self, elmt):
        logger.debug(f"Date {self.name or self.interface} will parse {elmt!r}")
        if isinstance(elmt, str):
            dateobj = parse_date(elmt)
            return dateobj
        return elmt

    def __repr__(self):
        return f"SerializerDate({self.interface!r}, constructor= <ISO date parser>)"


class SerializerDateTime(SerializerField):
    def __init__(self, interface, constructor=None, default=None, optional=True, name=None):
        super().__init__(interface, constructor=constructor or self._constructor, default=default, optional=optional, name=name)

    def _constructor(self, elmt):
        logger.debug(f"DateTime {self.name or self.interface} will parse {elmt!r}")
        if isinstance(elmt, str):
            dateobj = parse_datetime(elmt)
            if dateobj is None:
                # Try if date only works instead
                dateobj = parse_date(elmt)
            return dateobj
        return elmt

    def __repr__(self):
        return f"SerializerDateTime({self.interface!r}, constructor= <ISO datetime parser>)"


class SerializerMixin(SerializerBase):

    _fields = {}
    _rootless = False
    _strict = False
    _unique_ids = False
    _root_name = None
    _blueprint = None
    _structure = None

    def __init__(self, *args, **kwargs):
        args = dict(zip(self._fields.keys(), args))
        args.update(kwargs)
        for k, v in args.items():
            if self._strict and k not in self._fields:
                continue
            setattr(self, k, v)

    @classmethod
    def get_blueprint(cls):
        if cls._blueprint is None:
            cls.parse_structure()
        return cls._blueprint

    @classmethod
    def get_structure(cls):
        if cls._blueprint is None:
            cls.parse_structure()
        return cls._structure

    @classmethod
    def get_root_name(cls):
        if cls._root_name is None:
            cls._root_name = cls.__name__.lower()
        return cls._root_name

    @classmethod
    def parse_structure(cls):
        cls._blueprint = dict()
        cls._structure = dict()
        for k, v in cls._fields.items():
            if isinstance(v, type):
                field = SerializerField(interface=k,
                                        constructor=v,
                                        name=k,)
            elif isinstance(v, SerializerField):
                logger.debug(f'=====> Parsing got a field:{v!r}')
                field = v
                field.name = k      # Forces a name while parsing in the case it has not been provided
            elif isinstance(v, list) or isinstance(v, tuple):
                field = SerializerField(interface=v[0],
                                        constructor=v[1] if len(v) > 1 else None,
                                        default=v[2] if len(v) > 2 else None,
                                        optional=v[3] if len(v) > 3 else True,
                                        name=k)
            else:
                field = SerializerField(interface=v, name=k)

            cls._blueprint[field.interface] = field
            cls._structure[field.name] = field

    @classmethod
    def from_structure(cls, elmt):
        return from_structure(cls, elmt)

    @classmethod
    @requires('xmltodict')
    def from_xml(cls, xml, *args, **kwargs):
        root = cls.get_root_name()
        d = xmltodict.parse(xml, dict_constructor=dict, *args, **kwargs)
        return cls.from_structure(d[root])

    def as_structure(self, use_internal_names=False):
        structure = self.get_structure()
        return to_structure(self.__dict__, structure=structure, strict=self._strict, use_internal_names=use_internal_names)

    @requires('dicttoxml')
    def as_xml(self, use_internal_names=False):
        return dicttoxml.dicttoxml(self.as_structure(use_internal_names=use_internal_names),
                                   root=not self._rootless,
                                   custom_root=None if self._rootless else self.get_root_name(),
                                   attr_type=False,
                                   ids=self._unique_ids)

    def __str__(self):
        return "\n".join([f" {k}: {getattr(self,k)}" for k in self.get_structure() if not k.startswith("_")])


class SerializerStrictMixin(SerializerMixin):
    _strict = True


class SerializerRootlessMixin(SerializerMixin):
    _rootless = True
