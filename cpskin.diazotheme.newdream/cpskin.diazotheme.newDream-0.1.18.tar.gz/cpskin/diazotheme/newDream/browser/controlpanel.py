# -*- coding: utf-8 -*-

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from cpskin.core.browser.controlpanel import CPSkinControlPanel
from cpskin.core.interfaces import ICPSkinSettings
from cpskin.diazotheme.newDream.interfaces import INewDreamSettings
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements


class NewDreamControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(INewDreamSettings)

    def __init__(self, context):
        super(NewDreamControlPanelAdapter, self).__init__(context)
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(INewDreamSettings, False)

    def getBreadCrumbsAboveTitle(self):
        return self.settings.breadcrumbs_below_title

    def setBreadCrumbsAboveTitle(self, value):
        self.settings.breadcrumbs_below_title = value

    breadcrumbs_below_title = property(
        getBreadCrumbsAboveTitle, setBreadCrumbsAboveTitle
    )


class NewDreamControlPanel(CPSkinControlPanel):

    form_fields = form.FormFields(ICPSkinSettings) + form.FormFields(INewDreamSettings)
