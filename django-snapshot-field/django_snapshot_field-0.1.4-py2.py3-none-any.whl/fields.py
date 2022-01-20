# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

import six
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import smart_str

from snapshot_field.utils import get_model_class, get_fields_from_model, get_translated_fields, \
    deserialize_object_json, serialize_object_json
from .compat import get_label_lower

translator = None
try:
    from modeltranslation.translator import translator, NotRegistered # noqa
    from modeltranslation.utils import build_localized_fieldname # noqa
except ImportError:
    pass

PolymorphicModel = None
try:
    from polymorphic.models import PolymorphicModel # noqa
except ImportError:
    pass


class SnapshotModelField(models.TextField):
    """
    """

    def __init__(self,
                 models=None,
                 immutable=True,
                 *args, **kwargs):
        """

        :param models: list of models or list of tuple[Model, {'fields': ['id'], 'refs': ['ref']}]
        :param immutable:
        :param args:
        :param kwargs:
        """

        kwargs['editable'] = False
        if isinstance(models, str):
            models = [models]
        self.models = models
        self.depth = kwargs.pop('depth', 0)
        self.serializer_kwargs = kwargs.pop('serializer_kwargs', None) or {}

        super(SnapshotModelField, self).__init__(*args, **kwargs)

    def _get_model_map(self):
        model_map = getattr(self, '__model_map', None)
        if model_map:
            return model_map

        model_map = {}
        if self.models:
            for model in self.models:
                opts = {}
                if isinstance(model, (tuple, list)):
                    model, opts = model
                model_parts = model.split('.')
                if len(model_parts) == 1:
                    model = '.'.join(
                        [self.model._meta.app_label] + model_parts)
                model_class = get_model_class(model)
                label_lower = get_label_lower(model_class._meta)
                model_map[label_lower] = {
                    'model': model_class,
                    'opts': opts
                }
        setattr(self, '__model_map', model_map)
        return model_map

    model_map = property(_get_model_map)

    def _get_model_opts(self, model):
        try:
            label_lower = get_label_lower(model._meta)
            return self.model_map[label_lower]['opts']
        except KeyError:
            return None

    def get_snapshot_opts(self, model):
        model_class = get_model_class(model)
        opts = self._get_model_opts(model_class)
        fields = None
        refs = None
        if opts:
            fields = opts.get('fields')
            refs = opts.get('refs')

        if not fields:
            fields = list(get_fields_from_model(model_class).keys())

        trans_field_map = get_translated_fields(model, fields)
        # fields = list(set(fields) - set(trans_field_map))
        map(fields.extend, trans_field_map.values())
        return dict(
            fields=list(set(fields)),
            refs=refs,
        )

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super(SnapshotModelField, self).contribute_to_class(cls, name, *args, **kwargs)
        # Add our descriptor to this field in place of of the normal attribute
        setattr(cls, self.name, ProxyFieldDescriptor(self.name))

    def validate_snapshot_model(self, model):
        if not self.models:
            return
        model_class = get_model_class(model)
        label_lower = get_label_lower(model_class._meta)
        if label_lower not in self.model_map:
            raise ValidationError('Invalid model. Expect %s' %
                                  ', '.join(["'%s'" % self.model_map.keys()]))

    def validate(self, value, model_instance):
        if not value:
            return
        if not isinstance(value, models.Model):
            raise ValidationError("Need model instance")
        self.validate_snapshot_model(value._meta.concrete_model)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value and not isinstance(value, models.Model):
            raise ValueError("Need model instance")

        if value is None:
            return None
        if isinstance(value, six.string_types):
            # maybe serialized
            return value
        model_class = value._meta.concrete_model
        opts = self.get_snapshot_opts(model_class)
        if PolymorphicModel is not None:
            if isinstance(value, PolymorphicModel):
                # hack for polymorphic model
                model_class._meta = copy.copy(
                    model_class._meta)
                model_class._meta.local_fields = model_class._meta.fields
        return serialize_object_json(value, **opts)

    def from_db_value(self, value, *args, **kwargs):
        if value is None:
            return value
        return deserialize_object_json(value)

    def to_python(self, value):
        if isinstance(value, six.string_types):
            return deserialize_object_json(value)
        return value


class ProxyFieldDescriptor(object):
    def __init__(self, field_name, proxy_class=None):
        self.field_name = field_name

    def __get__(self, instance=None, owner=None):
        # grab the original value before we proxy
        value = instance.__dict__[self.field_name]
        return value

    def __set__(self, instance, value):
        if isinstance(value, models.Model):
            value = ModelProxy(value)
        instance.__dict__[self.field_name] = value


class Proxy(object):
    __slots__ = ["_obj", "__weakref__"]

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    #
    # proxying (special cases)
    #
    def __getattribute__(self, name):
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self):
        return bool(object.__getattribute__(self, "_obj"))

    def __str__(self):
        return str(object.__getattribute__(self, "_obj"))

    def __repr__(self):
        return repr(object.__getattribute__(self, "_obj"))

    #
    # factories
    #
    _special_names = [
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
        '__truediv__', '__xor__', 'next',
        '__unicode__'
    ]

    @classmethod
    def _create_class_proxy(cls, theclass, _callable=False):
        """creates a proxy for the given class"""

        def make_method(name):
            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, "_obj"), name)(*args, **kw)

            return method

        namespace = {}
        special_names = set(cls._special_names)
        if not _callable:
            special_names -= {'__call__'}
        for name in special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        class_name = smart_str("%s(%s)" % (cls.__name__, theclass.__name__))
        return type(class_name, (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """
        creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
        passed to this class' __init__, so deriving classes can define an
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(
                obj.__class__, _callable=callable(obj))
        ins = object.__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)
        return ins


class ModelProxy(Proxy):
    def __getattribute__(self, item):
        if item == 'prepare_database_save':
            raise AttributeError()
        return super(ModelProxy, self).__getattribute__(item)
