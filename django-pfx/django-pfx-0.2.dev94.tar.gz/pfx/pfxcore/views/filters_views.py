import re
from datetime import date
from functools import reduce

from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class FilterGroup():
    def __init__(self, name, label, filters):
        self.name = name
        self.label = label
        self.filters = filters

    @property
    def meta(self):
        return dict(name=self.name, label=self.label, items=[
            f.meta for f in self.filters
        ])

    def query(self, params):
        return Q(*[f.query(params) for f in self.filters])


class Filter():
    BooleanField = "BooleanField"
    IntegerField = "IntegerField"
    FloatField = "FloatField"
    CharField = "CharField"
    DateField = "DateField"
    ForeignKey = "ForeignKey"

    RE_FALSE = re.compile(r'^(0|false|)$', re.IGNORECASE)

    def __init__(
            self, name, label, type=None, filter_func=None, choices=None,
            related_model=None):
        self.name = name
        self.label = label
        self.type = type
        self.filter_func = filter_func
        self.choices = choices
        self.related_model = related_model

    @property
    def meta(self):
        res = dict(
            label=_(self.label),
            name=self.name,
            type=self.type)
        if self.choices:
            res['choices'] = [
                dict(label=_(v), value=k) for k, v in self.choices]
        if self.related_model:
            res['related_model'] = self.related_model
        return res

    def _parse_value(self, value):
        if self.type == Filter.BooleanField:
            return value and not Filter.RE_FALSE.match(value)
        if self.type in (Filter.IntegerField, Filter.ForeignKey):
            return value and int(value) or None
        if self.type == Filter.FloatField:
            return value and float(value) or None
        if self.type == Filter.DateField:
            return value and date.fromisoformat(value) or None
        return value

    def query(self, params):
        values = [self._parse_value(v) for v in params.getlist(self.name)]
        if values:
            return reduce(
                lambda x, y: x | y, [self.filter_func(v) for v in values])
        return Q()


class ModelFilter(Filter):
    def __init__(
            self, model, name, label=None, type=None, filter_func=None,
            choices=None, related_model=None):
        self.model = model
        self.field = model._meta.get_field(name)
        super().__init__(
            name, label or self.field.verbose_name,
            type or self.field.get_internal_type(), filter_func,
            choices or self.field.choices, related_model or (
                self.field.remote_field and
                self.field.remote_field.model.__name__))

    @property
    def meta(self):
        res = dict(
            label=_(self.label), name=self.name, type=self.type)
        if self.choices:
            res['choices'] = [
                dict(label=_(v), value=k) for k, v in self.choices]
        if self.related_model:
            res['related_model'] = self.related_model
        return res

    def query(self, params):
        values = [self._parse_value(v) for v in params.getlist(self.name)]
        if self.filter_func and values:
            return reduce(
                lambda x, y: x | y, [self.filter_func(v) for v in values])
        elif values:
            return reduce(
                lambda x, y: x | y, [Q(**{self.name: v}) for v in values])
        return Q()
