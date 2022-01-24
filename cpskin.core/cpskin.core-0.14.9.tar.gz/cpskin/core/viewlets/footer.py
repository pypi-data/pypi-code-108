# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class CPSkinFooterSitemapViewlet(ViewletBase):
    render = ViewPageTemplateFile('footersitemap.pt')

    def showSiteMap(self):
        return api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.show_footer_sitemap')

    def createSiteMap(self):
        context = aq_inner(self.context)
        # take the 2 first levels of the site that respect the navigation
        # strategy
        portal_catalog = getToolByName(context, 'portal_catalog')
        navtreeProps = getToolByName(
            context, 'portal_properties').navtree_properties
        queryDict = {}
        navigation_root = api.portal.get_navigation_root(context)
        queryDict['path'] = {
            'query': '/'.join(navigation_root.getPhysicalPath()), 'depth': 1}
        if navtreeProps.enable_wf_state_filtering:
            queryDict['review_state'] = navtreeProps.wf_states_to_show
        queryDict['sort_on'] = 'getObjPositionInParent'
        themes = portal_catalog(queryDict)
        res = []
        metaTypesNotToList = navtreeProps.metaTypesNotToList
        idsNotToList = navtreeProps.idsNotToList
        for theme in themes:
            if theme.meta_type not in metaTypesNotToList and \
                    theme.id not in idsNotToList and not theme.exclude_from_nav:
                themeRes = {'theme': theme, 'children': []}
                # do a second catalog_search by theme
                queryDict['path'] = {'query': theme.getPath(), 'depth': 1}
                children = portal_catalog(queryDict)
                for child in children:
                    if child.meta_type not in metaTypesNotToList and \
                            child.id not in idsNotToList and not child.exclude_from_nav:
                        themeRes['children'].append(child)
                res.append(themeRes)
        return res

    def getFooterText(self):
        navigation_root = api.portal.get_navigation_root(self.context)
        footer_static = getattr(navigation_root, 'footer-static', None)
        text = ''
        if footer_static is None:
            return
        if footer_static.Language() == self.context.Language():
            if getattr(footer_static, 'text', None):
                text = footer_static.text.raw
                return text
        if getattr(footer_static, 'getTranslation', None):
            lang = self.context.REQUEST.get('LANGUAGE', 'fr')
            footer_static = footer_static.getTranslation(lang)
        if getattr(footer_static, 'text', None):
            text = footer_static.text.raw
        return text
