# -*- coding: utf-8 -*-
"""
imio.annex
----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.component.interfaces import ObjectEvent
from zope.interface import implements

from imio.annex.interfaces import IAnnexFileChangedEvent
from imio.annex.interfaces import IConversionStartedEvent


class AnnexFileChangedEvent(ObjectEvent):
    implements(IAnnexFileChangedEvent)

    def __init__(self, object, file, called_by=None):
        """p_called_by can be used by notifier to specify where it was notified
           and so handlers may check this value and behave accordingly."""
        super(AnnexFileChangedEvent, self).__init__(object)
        self.file = file
        self.called_by = called_by


class ConversionStartedEvent(ObjectEvent):
    implements(IConversionStartedEvent)
