# -*- coding: utf-8 -*-
"""
cpskin.core
-----------

Created by mpeeters
:copyright: (c) 2015 by Affinitic SPRL
:license: GPL, see LICENCE.txt for more details.
"""


from eea.facetednavigation.subtypes.interfaces import IPossibleFacetedNavigable


class ICPSkinPossibleFacetedNavigable(IPossibleFacetedNavigable):
    """
    Marker interface for all objects that should have the ability to be
    faceted navigable
    """
