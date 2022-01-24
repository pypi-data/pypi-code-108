# -*- coding: utf-8 -*-
"""
imio.annex
----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IImioAnnexLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAnnexFileChangedEvent(Interface):
    pass


class IConversionStartedEvent(Interface):
    pass
