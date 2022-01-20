# -*- coding: utf-8 -*-
from zope.component import adapter
from zope.interface import implementer
from plone.app.dexterity.permissions import GenericFormFieldPermissionChecker
from rer.sitesearch.interfaces import IRerSiteSearchSettingsForm


try:
    from plone.app.z3cform.interfaces import IFieldPermissionChecker
except ImportError:
    # bbb for < plone 5.2rc2
    from plone.app.widgets.interfaces import IFieldPermissionChecker


@adapter(IRerSiteSearchSettingsForm)
@implementer(IFieldPermissionChecker)
class SiteSearchSettingsPermissionChecker(GenericFormFieldPermissionChecker):
    """ """

    def validate(self, field_name, vocabulary_name=None):
        if field_name in ["types"]:
            return True
        return super(SiteSearchSettingsPermissionChecker, self).validate(
            field_name, vocabulary_name
        )
