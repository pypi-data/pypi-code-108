# -*- coding: utf-8 -*-
"""
cpskin.core
-----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone.z3cform.textlines.textlines import TextLinesWidget
from z3c.form import util
from z3c.form.converter import BaseDataConverter
from z3c.form.widget import FieldWidget
from zope.component import adapts
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import ISequence

import six


class IMultiLineWidget(Interface):
    pass


@implementer(IMultiLineWidget)
class MultiLineWidget(TextLinesWidget):
    pass


class MultiLineDataConverter(BaseDataConverter):
    adapts(ISequence, IMultiLineWidget)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return ['']
        if isinstance(value, six.string_types):
            return [util.toUnicode(value)]
        return [util.toUnicode(v) for v in value if v]

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if self._strip_value and isinstance(value, six.string_types):
            value = [value.strip()]

        if value == u'' or value == []:
            return self.field.missing_value

        return [v for v in value if v]


def multiline_field_widget(field, request):
    return FieldWidget(field, MultiLineWidget(request))
