# -*- coding: utf-8 -*-
from imio.gdpr import _
from imio.gdpr.interfaces import IGDPRSettings
from plone.app.registry.browser import controlpanel


class GDPRSettingsEditForm(controlpanel.RegistryEditForm):
    """Control panel edit form."""

    schema = IGDPRSettings
    label = _(u'GDPR settings')
    description = _(u'Show GDPR explanation.')

    def updateFields(self):
        super(GDPRSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(GDPRSettingsEditForm, self).updateWidgets()


class GDPRSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Control panel form wrapper."""

    form = GDPRSettingsEditForm
