# -*- coding: utf-8 -*-

from cpskin.minisite.interfaces import IInPortal
from plone import api
from plone.app.layout.viewlets import common


class TopCollapseViewlet(common.ViewletBase):

    def available(self):
        if not IInPortal.providedBy(self.request):
            return False
        return api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.collapse_minisite_menu',
            default=False,
        )
