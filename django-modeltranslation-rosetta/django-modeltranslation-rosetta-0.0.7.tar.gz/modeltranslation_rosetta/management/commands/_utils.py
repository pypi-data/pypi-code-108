# coding: utf-8
from __future__ import unicode_literals

from django.db.models import Model


def get_opts_from_model(model):
    fields = [(f.name, None) for f in model._meta.get_fields()]
    return dict(
        app_label=model._meta.app_label,
        model_name=model._meta.model_name,
        fields=fields,
    )


def parse_model(model):
    return dict(
        zip(["app_label", "model", "field"], model.lower().split(".") + [None] * 2)
    )


def has_exclude(model_opts, excludes):
    """

    :param model_opts: {app_label, model_name, fields}
    :param excludes: {app_label, model, field}
    :return:
    """
    if not excludes:
        return False

    if issubclass(model_opts, Model) or isinstance(model_opts, Model):
        model_opts = get_opts_from_model(model_opts)

    app_label = model_opts["app_label"]
    model_name = model_opts["model_name"]
    fields = list(model_opts["fields"])

    _exclude = False
    for i in excludes:
        _exclude |= i["app_label"] == app_label and i["model"] is None
        _exclude |= (
            i["app_label"] == app_label
            and i["model"] == model_name
            and i["field"] is None
        )

        for f, tr_f in fields:
            if (
                i["app_label"] == app_label
                and i["model"] == model_name
                and i["field"] == f
            ):
                del fields[f]

    return _exclude or not fields


def has_include(model_opts, includes):
    if not includes:
        return True

    if issubclass(model_opts, Model) or isinstance(model_opts, Model):
        model_opts = get_opts_from_model(model_opts)

    app_label = model_opts["app_label"]
    model_name = model_opts["model_name"]
    fields = list(model_opts["fields"])

    _include = False
    for i in includes:
        _include |= i["app_label"] == app_label and i["model"] is None
        _include |= (
            i["app_label"] == app_label
            and i["model"] == model_name
            and i["field"] is None
        )
        for f, tr_f in fields:
            if (
                i["app_label"] == app_label
                and i["model"] == model_name
                and i["field"]
                and i["field"] != f
            ):
                del fields[f]

    return _include and fields
