# coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict

from django.conf import settings
from django.db.models import Model
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname


def build_model_name(model):
    return "%s.%s" % (model._meta.app_label, model._meta.model_name)


def get_model(model_name):
    return get_models()[model_name]


def get_models():
    models_map = OrderedDict()
    models = translator.get_registered_models(abstract=False)
    for model in models:
        opts = translator.get_options_for_model(model)
        model_key = build_model_name(model)
        models_map[model_key] = {
            "model": model,
            "meta": model._meta,
            "opts": opts,
            "model_key": model_key,
        }

    return models_map


def get_opts_from_model(model, fields=None):
    opts = translator.get_options_for_model(model)
    meta = model._meta

    trans_fields = {
        field_name: {
            lang: build_localized_fieldname(field_name, lang)
            for lang, _ in settings.LANGUAGES
        }
        for field_name in opts.fields.keys()
        if not fields or field_name in fields
    }

    model_key = "%s.%s" % (meta.app_label, meta.model_name)
    model_opts = dict(
        model=model,
        fields=trans_fields,
        app_label=meta.app_label,
        model_name=meta.model_name,
        model_key=model_key,
        opts=opts,
    )
    return model_opts


def parse_model(model):
    return dict(
        zip(["app_label", "model", "field"], model.lower().split(".") + [None] * 2)
    )


def has_exclude(model_opts, excludes):
    """

    :param model_opts: {app_label, model_name, fields}
    :param excludes: <list> of {app_label, model, field}
    :return:
    """

    if issubclass(model_opts, Model) or isinstance(model_opts, Model):
        model_opts = get_opts_from_model(model_opts)

    app_label = model_opts["app_label"]
    model_name = model_opts["model_name"]
    fields = list(model_opts["fields"])

    if not excludes:
        return {"match": False, "fields": model_opts["fields"]}

    _exclude = False
    for i in excludes:
        _exclude |= i["app_label"] == app_label and i["model"] is None
        _exclude |= (
            i["app_label"] == app_label
            and i["model"] == model_name
            and i["field"] is None
        )

        for k, f in enumerate(fields):
            if (
                i["app_label"] == app_label
                and i["model"] == model_name
                and i["field"] == f
            ):
                del fields[k]

    return {"match": _exclude or not fields, "fields": fields}


def has_include(model_opts, includes):
    """

    :param model_opts: {app_label, model_name, fields}
    :param includes: <list> of {app_label, model, field}
    :return:
    """

    if issubclass(model_opts, Model) or isinstance(model_opts, Model):
        model_opts = get_opts_from_model(model_opts)

    app_label = model_opts["app_label"]
    model_name = model_opts["model_name"]
    fields = list(model_opts["fields"])

    if not includes:
        return {"match": True, "fields": model_opts["fields"]}

    _include = False
    delete_fields = set()
    for i in includes:
        _include |= i["app_label"] == app_label and i["model"] is None
        _include |= (
            i["app_label"] == app_label
            and i["model"] == model_name
            and i["field"] is None
        )

        for k, f in enumerate(fields):
            _include |= bool(
                i["app_label"] == app_label
                and i["model"] == model_name
                and i["field"]
                and i["field"] == f
            )
            if (
                i["app_label"] == app_label
                and i["model"] == model_name
                and i["field"]
                and i["field"] != f
            ):
                delete_fields.add(f)

    fields = list(set(fields) - delete_fields)
    return {"match": _include and fields, "fields": fields}


def get_cleaned_fields(model_opts, excludes=None, includes=None):
    """

    :param model_opts: model_opts or model
    :param excludes: list of app or  app.Model or app.Model.field
    :param includes: list of app or  app.Model or app.Model.field
    :return: list of allowed fields
    """
    exclude = has_exclude(model_opts, excludes)
    if exclude["match"]:
        return None

    include = has_include(model_opts, includes)
    if not include["match"]:
        return None

    return list(set(include["fields"]) & set(exclude["fields"]))
