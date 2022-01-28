#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


import datetime
from itertools import groupby

import arrow
from django.conf import settings
from django.forms.models import ModelChoiceIterator, ModelChoiceField, ModelMultipleChoiceField


class IsoDateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()

    def to_url(self, value):
        return str(value)


def get_display_age_group_in_presence():
    return getattr(settings, 'DISPLAY_AGE_GROUP_IN_PRESENCE', False)


def range_time(add_hour, add_minute, start_from_sh, start_from_sm):
    now = arrow.utcnow().to('Europe/Paris').replace(hour=start_from_sh, minute=start_from_sm, second=0, microsecond=0)
    end = now.shift(hours=+add_hour)

    lt = []
    while now <= end:
        l = [now.time(), now.datetime.strftime("%HH%M")]
        now = now.shift(minutes=+add_minute)
        tuple_l = tuple(l)
        lt.append(tuple_l)
    tuple_lt = tuple(lt)
    return tuple_lt


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


class Grouped(object):
    def __init__(self, queryset, group_by_field,
                 group_label=None, *args, **kwargs):
        """
        ``group_by_field`` is the name of a field on the model to use as
                           an optgroup.
        ``group_label`` is a function to return a label for each optgroup.
        """
        super(Grouped, self).__init__(queryset, *args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset.all()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, choices in groupby(self.queryset.all(),
                                      key=lambda row: getattr(row, self.field.group_by_field)):
            if self.field.group_label(group):
                yield (
                    self.field.group_label(group),
                    [self.choice(ch) for ch in choices]
                )


class GroupedModelChoiceField(Grouped, ModelChoiceField):
    choices = property(Grouped._get_choices, ModelChoiceField._set_choices)


class GroupedModelMultiChoiceField(Grouped, ModelMultipleChoiceField):
    choices = property(Grouped._get_choices, ModelMultipleChoiceField._set_choices)


def has_view_dailyfollowup(request):
    return request.user.has_perm('nobinobi_daily_follow_up.view_dailyfollowup')
