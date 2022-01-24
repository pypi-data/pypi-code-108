# -*- coding: utf-8 -*-
"""
imio.annex
----------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from plone import api


def is_iconified_categorized(portal_type):
    """
    Verify if the given portal_type have the IIconifiedCategorization behavior
    """
    portal_types = api.portal.get_tool('portal_types')
    pt = portal_types.get(portal_type)
    if not pt:
        return False
    behavior = ('collective.iconifiedcategory.behaviors.'
                'iconifiedcategorization.IIconifiedCategorization')
    return behavior in pt.behaviors
