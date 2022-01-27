# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from redturtle.chefcookie import _
from redturtle.chefcookie.interfaces import IChefCookieSettings
from redturtle.chefcookie.interfaces import IChefCookieSettingsConfigs
from redturtle.chefcookie.interfaces import IChefCookieSettingsLabels
from z3c.form import field
from z3c.form import group


class FormDefault(group.Group):
    label = _("settings_default_label", default=u"Settings")
    fields = field.Fields(IChefCookieSettingsConfigs)


class FormLabels(group.Group):
    label = _("settings_labels_label", default=u"Labels")
    fields = field.Fields(IChefCookieSettingsLabels)


class CookieSettingsControlPanel(controlpanel.RegistryEditForm):
    """ """

    schema = IChefCookieSettings
    groups = (FormDefault, FormLabels)

    id = "ChefcookieControlPanel"
    label = _(u"Chefcookie settings")
