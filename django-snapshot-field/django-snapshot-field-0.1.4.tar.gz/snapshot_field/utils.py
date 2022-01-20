import json
from collections import defaultdict

import six
from django.apps import apps
from django.conf import settings
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.core.serializers.python import _get_model
from django.db import models
from django.utils.translation import gettext_lazy as _

translator = None
try:
    from modeltranslation.translator import translator, NotRegistered
    from modeltranslation.utils import build_localized_fieldname
except ImportError:
    pass


def build_field_map(fields):
    """
    >>> build_field_map(['field1', 'field2'])
    {'field1': set(), 'field2': set()}
    >>> build_field_map(['field1', 'field2', 'field2__foo', 'field2__bar__bar2'])
    {'field1': set(), 'field2': {'bar__bar2', 'foo'}}
    >>> build_field_map([])
    {}


    :param fields:
    :return:
    """
    field_map = dict()
    for f in fields:
        f_parts = f.split("__")
        p_f = f_parts[0]
        s_f = f_parts[1:]
        if p_f not in field_map:
            field_map[p_f] = set()
        if s_f:
            field_map[p_f].add("__".join(s_f))
    return field_map


def serialize_object(obj, fields=None, refs=None):
    field_map = build_field_map(fields=fields or get_fields_from_model(obj))
    refs_map = build_field_map(fields=refs or [])
    _fields = list(field_map.keys())
    ser_obj = serializers.serialize("python", [obj], fields=_fields)[0]

    fk_fields = {
        f.name
        for f in obj._meta.fields
        if isinstance(f, (models.ForeignKey, models.OneToOneField))
    }
    refs = {}
    for f in fk_fields:
        if not fields or f in fields and f in refs_map:
            n_obj = getattr(obj, f)
            sub_fields = field_map.get(f)
            sub_refs = refs_map.get(f)
            if n_obj:
                refs[f] = serialize_object(n_obj, fields=sub_fields, refs=sub_refs)

    ser_obj["refs"] = refs
    return ser_obj


def serialize_object_json(obj, fields=None, refs=None):
    return json.dumps(
        serialize_object(obj, fields=fields, refs=refs), cls=DjangoJSONEncoder
    )


def prepare_object(value):
    # Fix and prepare object before deserialization
    _Model = _get_model(value["model"])
    fields = get_fields_from_model(_Model)
    for _field in list(value["fields"].keys()):
        if _field not in fields:
            del value["fields"][_field]
    return value


def _deserialize_object(value, serializer_kwargs=None):
    serializer_kwargs = serializer_kwargs or {}
    try:
        value = prepare_object(value)
        deser = list(serializers.deserialize("python", [value], **serializer_kwargs))[0]
        instance = deser.object
        instance.save_base = noop_func
        instance.save = noop_func
        instance.delete = noop_func
        return instance
    except ValueError:
        raise ValidationError(_("Enter valid JSON"))


def deserialize_object(value, serializer_kwargs=None):
    if isinstance(value, list):
        return [deserialize_object(v) for v in value]
    refs = value.pop("refs", None) or {}
    obj = _deserialize_object(value, serializer_kwargs)
    for name, ref_data in refs.items():
        sub_obj = deserialize_object(ref_data, serializer_kwargs)
        obj.__dict__[name] = sub_obj
        if hasattr(obj._state, "fields_cache"):
            obj._state.fields_cache[name] = sub_obj
        else:
            # Backward compatibly for django 1.11
            field = obj._meta.get_field(name)
            obj.__dict__[field.get_cache_name()] = sub_obj
    return obj


def deserialize_object_json(str_data, serializer_kwargs=None):
    data = json.loads(str_data)
    if isinstance(data, list):
        # Fallback for old data
        return deserialize_object(data, serializer_kwargs)[0]
    return deserialize_object(data, serializer_kwargs)


def noop_func(*a, **kw):
    return None


def get_model_class(model):
    if isinstance(model, six.string_types):
        model = apps.get_model(*model.split("."))
    return model


def get_fields_from_model(model):
    opts = model._meta.concrete_model._meta
    fields = {}
    for f in opts.fields:
        # if isinstance(f, RelatedField):
        #     continue
        fields[f.name] = f
    return fields


def get_translated_fields(model, fields):
    if not translator:
        return {}
    try:
        opts = translator.get_options_for_model(model)
    except NotRegistered:
        return {}

    trans_fields = defaultdict(list)
    for field_name in opts.fields.keys():
        if field_name not in fields:
            continue
        for lang, _s in settings.LANGUAGES:
            trans_fields[field_name].append(build_localized_fieldname(field_name, lang))
    return dict(trans_fields)
