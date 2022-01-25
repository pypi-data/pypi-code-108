# -*- coding: utf-8 -*-

from collective.anysurfer.interfaces import ILayerSpecific
from collective.folderishtypes.interfaces import IFolderishType
from cpskin.core.interfaces import ICPSkinSettings
from Acquisition import aq_parent
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import isDefaultPage
from Products.Five import BrowserView
from zope.component import getUtility
from plone import api


class UtilsView(BrowserView):

    def is_gdpr(self):
        return api.portal.get_registry_record(
            "imio.gdpr.interfaces.IGDPRSettings.is_text_ready", default=False
        )

    def has_enabled_accessibilty_link_in_footer(self):
        return api.portal.get_registry_record(
            "cpskin.core.interfaces.ICPSkinSettings.enable_accessibility_link_in_footer",
            default=False,
        )

    def edit_anysurfer_settings(self):
        if api.user.is_anonymous():
            return False
        current_user = api.user.get_current()
        roles = api.user.get_roles(username=current_user.getUserName())
        if "Manager" not in roles and "Site Administrator" not in roles:
            return False
        if not ILayerSpecific.providedBy(self.request):
            return False
        if bool(self.request.get("change_link_visibility", False)) is True:
            registry = getUtility(IRegistry)
            records = registry.records
            # cpskin.core.interfaces.ICPSkinSettings
            value = not records["cpskin.core.interfaces.ICPSkinSettings.enable_accessibility_link_in_footer"].value
            api.portal.set_registry_record(
                "enable_accessibility_link_in_footer", value, interface=ICPSkinSettings
            )
            self.request.response.redirect(self.context.absolute_url())
            self.request.response.setHeader('Cache-Control', 'no-cache, no-store')
        return True

    def has_folderish_default(self):
        if not IFolderishType.providedBy(self.context):
            return False
        return isDefaultPage(self.context, self.request)

    def convert_default_url(self, url, to_parent=False):
        """Converts url from default view url to parent or vice versa
        """
        obj_url = self.context.absolute_url()
        parent_url = aq_parent(self.context).absolute_url()
        if to_parent and obj_url in url:
            return url.replace(obj_url, parent_url)
        if not to_parent and obj_url not in url:
            return url.replace(parent_url, obj_url)
        return url
