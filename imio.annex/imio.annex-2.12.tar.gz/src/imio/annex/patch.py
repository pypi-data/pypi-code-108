# -*- coding: utf-8 -*-
"""
imio.annex
----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from collective.documentviewer.convert import Converter
from zope.event import notify
from imio.annex.events import ConversionStartedEvent


def converter_call(self, *args, **kwargs):
    notify(ConversionStartedEvent(self.context))
    return Converter._old___call__(self, *args, **kwargs)
