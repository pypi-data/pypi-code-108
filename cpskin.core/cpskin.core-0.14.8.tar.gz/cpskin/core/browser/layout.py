# -*- coding: utf-8 -*-
from DateTime import DateTime
from collective.anysurfer.layout import LayoutPolicy as AnysurferLayoutPolicy
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone import api
from plone.app.layout.globals import layout as base
from plone.app.layout.globals.interfaces import ILayoutPolicy
from plone.i18n.normalizer import IIDNormalizer
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.interface import implements

from cpskin.citizen.utils import is_citizen


class LayoutPolicy(AnysurferLayoutPolicy, base.LayoutPolicy):
    """
    Enhanced layout policy
    """
    implements(ILayoutPolicy)

    def bodyClass(self, template, view):
        """
        Extend Plone to add a CSS class on <body> based on :
        1. the 1st level folder of the current context :
         - 'section-theme1' or 'section-theme2' or ... for portal tabs folders
           based on their positions
         - section-notheme if not in a portal tab folder
        2. the citizen user
        3. minisite
        4. homepage
        5. the portal_type of the collection (if any)
        6. the expiration of the content
        7. the layout used for faceted navigations
        """
        context = self.context

        # Get default body classes
        body_class = base.LayoutPolicy.bodyClass(self, template, view)

        # Get 1st level folders appearing in navigation
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        navtreeProps = api.portal.get_tool(name='portal_properties').navtree_properties
        navigation_root = api.portal.get_navigation_root(context)
        queryDict = {}
        queryDict['path'] = {'query': '/'.join(navigation_root.getPhysicalPath()), 'depth': 1}
        if navtreeProps.enable_wf_state_filtering:
            queryDict['review_state'] = navtreeProps.wf_states_to_show
        queryDict['sort_on'] = 'getObjPositionInParent'
        queryDict['portal_type'] = 'Folder'
        queryDict['is_default_page'] = False
        brains = portal_catalog(queryDict)
        res = [b for b in brains if b.id not in navtreeProps.idsNotToList]

        # Get the first level of the current
        actual_url_path = '/'.join(context.getPhysicalPath())
        # Check if we are in a theme and check if we are in the right one (position)
        index = 1
        inTheme = False
        for brain in res:
            # checking startswith is not enough
            # see ticket #1227 :
            # if theme1 id is "theme" and theme2 id is "theme2", while being in the
            # theme2, it starts with 'theme' so it returns True to checking if being in theme 1...
            brainPath = brain.getPath()
            if actual_url_path.startswith(brainPath):
                brainPathLen = len(brainPath)
                if len(actual_url_path) == brainPathLen \
                   or actual_url_path[brainPathLen:brainPathLen + 1] == '/':
                    inTheme = True
                    body_class += ' section-theme%s' % index
            index += 1

        if not inTheme:
            body_class += ' section-notheme'

        header_class = api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.header_class'
        )
        if header_class:
            body_class += ' {0}'.format(header_class)

        navigation_class = api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.navigation_class'
        )
        if navigation_class:
            body_class += ' {0}'.format(navigation_class)

        content_columns_class = api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.columns_class'
        )
        if content_columns_class:
            body_class += ' {0}'.format(content_columns_class)

        footer_class = api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.footer_class'
        )
        if footer_class:
            body_class += ' {0}'.format(footer_class)

        minisite = self.request.get('cpskin_minisite', None)
        if minisite:
            if minisite.is_in_minisite_mode:
                body_class += ' in-minisite in-minisite-out-portal'
            elif minisite.is_in_portal_mode:
                body_class += ' in-minisite in-minisite-in-portal'

        if is_main_homepage(context):
            body_class += ' main-homepage'

        user = api.user.get_current()
        if is_citizen(user):
            body_class += ' user-citizen'

        if context.portal_type == 'Collection':
            normalizer = queryUtility(IIDNormalizer).normalize
            query = context.query
            portal_types = []
            if query is not None:
                for criteria in query:
                    if criteria.get('i') == 'portal_type':
                        portal_types = criteria.get('v')
            for portal_type in portal_types:
                body_class += ' collection-%s' % normalizer(portal_type)

        expiration_date = context.expiration_date
        if expiration_date and expiration_date < DateTime():
            body_class += ' expired-content'

        if IFacetedNavigable.providedBy(context):
            faceted_adapter = queryAdapter(context, IFacetedLayout)
            if faceted_adapter:
                body_class += ' %s' % faceted_adapter.layout

        return body_class


def is_main_homepage(context):
    homepage_types = ['LRF', 'Plone Site']
    if context.portal_type in homepage_types:
        return True
    return False
