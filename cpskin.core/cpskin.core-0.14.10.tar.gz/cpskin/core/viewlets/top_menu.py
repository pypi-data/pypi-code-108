# -*- coding: utf-8 -*-
from cpskin.core.interfaces import IElectedContentForTopMenu
from plone import api
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TopMenuViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('top_menu.pt')

    def menus(self):
        portal_catalog = api.portal.get_tool('portal_catalog')
        interface_name = IElectedContentForTopMenu.__identifier__
        query = {'object_provides': interface_name}
        results = portal_catalog.searchResults(query)
        results = [r for r in results if r.exclude_from_nav]
        menus = []
        for r in results:
            query_path = {'query': r.getPath(), 'depth': 1}
            query = {
                'path': query_path,
                'sort_on': 'getObjPositionInParent',
                'review_state': ('published_and_shown', )
            }
            sub_items = portal_catalog.searchResults(query)
            sub_items = [s for s in sub_items if not s.exclude_from_nav]
            menu_item = {
                'root': r,
                'submenu': sub_items,
            }
            menus.append(menu_item)
        return menus

    def show_lead_image(self):
        portal_registry = api.portal.get_tool('portal_registry')
        return portal_registry['cpskin.core.interfaces.ICPSkinSettings.show_leadimage_in_action_menu']  # noqa
