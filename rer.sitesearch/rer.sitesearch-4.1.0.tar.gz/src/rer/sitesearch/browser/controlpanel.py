# -*- coding: utf-8 -*-
from collective.z3cform.jsonwidget.browser.widget import JSONFieldWidget
from plone.app.registry.browser import controlpanel
from Products.CMFPlone.resources import add_bundle_on_request
from rer.sitesearch import _
from rer.sitesearch.interfaces import IRERSiteSearchSettings
from rer.sitesearch.interfaces import IRerSiteSearchSettingsForm
from rer.sitesearch.interfaces.settings import IIndexesRowSchema
from rer.sitesearch.interfaces.settings import ITypesMappingRowSchema
from z3c.form import field
from zope.interface import implementer


class RERSiteSearchSettingsEditForm(controlpanel.RegistryEditForm):
    """ """

    schema = IRERSiteSearchSettings
    id = "RERSiteSearchSettingsEditForm"
    label = _(u"Site Search settings")
    description = _(
        u"help_sitesearch_settings_editform",
        default=u"Set site search configurations",
    )

    fields = field.Fields(IRERSiteSearchSettings)
    fields["types_grouping"].widgetFactory = JSONFieldWidget
    fields["available_indexes"].widgetFactory = JSONFieldWidget

    def updateWidgets(self):
        """
        Hide some fields
        """
        super(RERSiteSearchSettingsEditForm, self).updateWidgets()
        self.widgets["types_grouping"].schema = ITypesMappingRowSchema
        self.widgets["available_indexes"].schema = IIndexesRowSchema


@implementer(IRerSiteSearchSettingsForm)
class RERSiteSearchSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """ """

    def __call__(self):
        add_bundle_on_request(self.request, "z3cform-jsonwidget-bundle")
        return super(RERSiteSearchSettingsControlPanel, self).__call__()

    form = RERSiteSearchSettingsEditForm
