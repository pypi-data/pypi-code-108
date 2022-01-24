# -*- coding: UTF-8 -*-
# Copyright 2021-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db.models import ForeignKey
from lino.core.choicelists import ChoiceListField, ChoiceList

def get_serializer_for_model(Model, options={}):
    from rest_framework import serializers
    from .fields import ChoiceField

    fks = []
    clfs = []
    for fld in Model._meta.fields:
        if isinstance(fld, ForeignKey):
            fks.append(fld)
        elif isinstance(fld, ChoiceListField):
            clfs.append(fld)

    meta_attrs = {
        'model': Model,
    }

    if options.get('fields', None) is not None:
        meta_attrs['fields'] = options['fields']
    else:
        meta_attrs['fields'] = '__all__'

    attrs_dict = dict(Meta=type('Meta', (type, ), meta_attrs))

    if options.get('extra_fields', None) is not None:
        attrs_dict.update(options['extra_fields'])

    for fld in clfs:
        attrs_dict[fld.name] = ChoiceField(choicelist=fld.choicelist)

    Serializer = type('Serializer', (serializers.ModelSerializer, ), attrs_dict)
    return Serializer
