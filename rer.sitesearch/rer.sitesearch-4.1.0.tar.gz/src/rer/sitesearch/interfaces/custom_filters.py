# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class ISiteSearchCustomFilters(Interface):
    """Marker interface"""

    label = Attribute("The label shown in the select")

    def __init__(context, request):
        """Adapts context and the request."""

    def __call__():
        """ """
