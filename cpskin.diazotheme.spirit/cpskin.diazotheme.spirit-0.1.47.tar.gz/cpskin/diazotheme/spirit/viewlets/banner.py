# -*- coding: utf-8 -*-

from plone import api

from cpskin.core.viewlets.banner import CPSkinBannerViewlet


class CPSkinSpiritBannerViewlet(CPSkinBannerViewlet):

    def slogan(self):
        default = {
            'title': "",
            'description': "",
        }
        navigation_root = api.portal.get_navigation_root(self.context)
        banner = getattr(navigation_root, 'banner.jpg', None)
        if not banner:
            return default
        return {
            'title': banner.Title(),
            'description': banner.Description(),
        }
