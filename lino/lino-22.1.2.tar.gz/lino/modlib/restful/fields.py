# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from rest_framework import serializers

class ChoiceField(serializers.ChoiceField):

    def __init__(self, choicelist, **kwargs):
        self.choicelist = choicelist
        super().__init__(choices=choicelist.choices, **kwargs)

    def to_representation(self, value):
        return {'text': str(value.text), 'value': value.value}

    def to_internal_value(self, data):
        return self.choicelist.to_python(data['value'])
