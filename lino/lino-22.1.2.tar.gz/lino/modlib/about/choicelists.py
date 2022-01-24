# Copyright 2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import six
import pytz

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from lino.core.choicelists import ChoiceList, Choice

class TimeZone(Choice):
    def __init__(self, *args, **kwargs):
        super(TimeZone, self).__init__(*args, **kwargs)
        self.tzinfo = pytz.timezone(six.text_type(self.text))

class TimeZones(ChoiceList):
    verbose_name = _("Time zone")
    verbose_name_plural = _("Time zones")
    item_class = TimeZone

add = TimeZones.add_item
add('01', settings.TIME_ZONE or 'UTC', 'default')


class DateFormat(Choice):
    extjs_format = None
    strftime_format = None
    primereact_format = None
    def __init__(self, value, extjs_format, strftime_format, primereact_format, name=None):
        text = primereact_format
        super(DateFormat, self).__init__(value, text, name)
        self.extjs_format = extjs_format
        self.strftime_format = strftime_format
        self.primereact_format = primereact_format


class DateFormats(ChoiceList):
    verbose_name = _("Date format")
    verbose_name_plural = _("Date formats")
    item_class = DateFormat

add = DateFormats.add_item
add('010', 'd.m.y', '%d.%m.%y', "dd.mm.y", 'default')
add('020', 'd.m.Y', '%d.%m.%Y', "dd.mm.yy")
add('030', 'd/m/y', '%d/%m/%y', "dd/mm/y")
add('040', 'd/m/Y', '%d/%m/%Y', "dd/mm/yy")
