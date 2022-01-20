# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from plone import api


class DiazoView(BrowserView):
    def is_breadcrumbs_below_title(self):
        return api.portal.get_registry_record(
            "cpskin.diazotheme.newDream.interfaces.INewDreamSettings.breadcrumbs_below_title"
        )
