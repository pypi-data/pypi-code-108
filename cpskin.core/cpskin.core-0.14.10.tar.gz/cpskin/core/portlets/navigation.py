# -*- coding: utf-8 -*-
from cpskin.minisite.browser.interfaces import IHNavigationActivated
from cpskin.minisite.interfaces import IInMinisiteBase
from cpskin.minisite.utils import get_minisite_navigation_level
from cpskin.minisite.utils import get_minisite_object
from plone import api
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.portlets.portlets.navigation import getRootPath
from plone.app.portlets.portlets.navigation import INavigationPortlet
from plone.app.portlets.portlets.navigation import NavtreeStrategy
from plone.app.portlets.portlets.navigation import QueryBuilder
from plone.app.portlets.portlets.navigation import Renderer
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


HAS_MENU = False
try:
    from cpskin.menu.interfaces import IFourthLevelNavigation
    HAS_MENU = True
except ImportError:
    pass


def calculateTopLevel(context, portlet, request=None):
    """Calculate top level of navigation menu to take care of 4th level menu
    NB : IFourthLevelNavigation is activated on the third level folder
    """
    if portlet.topLevel != 3 or not HAS_MENU:
        return portlet.topLevel
    portal = api.portal.get()
    contextPhyPath = context.getPhysicalPath()
    portalPhyPath = portal.getPhysicalPath()
    path = [elem for elem in list(contextPhyPath) if elem not in list(portalPhyPath)]  # noqa
    depth = len(path)
    if depth >= 3 and 'dexterity-types' not in path:
        subLevels = depth - 3
        if subLevels:
            thirdLevelPath = '/'.join(contextPhyPath[:-subLevels])
        else:
            thirdLevelPath = '/'.join(contextPhyPath)
        thirdLevelFolder = portal.unrestrictedTraverse(thirdLevelPath)
        if IFourthLevelNavigation.providedBy(thirdLevelFolder):
            return 4
        if request:
            if IInMinisiteBase.providedBy(request):
                minisite_obj = get_minisite_object(request)
                if minisite_obj and IHNavigationActivated.providedBy(minisite_obj):  # noqa
                    return get_minisite_navigation_level(minisite_obj) + 1
    return portlet.topLevel


class CPSkinQueryBuilder(QueryBuilder):
    implements(INavigationQueryBuilder)
    adapts(Interface, INavigationPortlet)

    def __call__(self):
        topLevel = calculateTopLevel(self.context, self.portlet)
        self.query['path']['navtree_start'] = topLevel + 1
        return self.query


class CPSkinNavtreeStrategy(NavtreeStrategy):
    implements(INavtreeStrategy)
    adapts(Interface, INavigationPortlet)

    def __init__(self, context, portlet):
        NavtreeStrategy.__init__(self, context, portlet)
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        currentFolderOnly = portlet.currentFolderOnly or \
            navtree_properties.getProperty('currentFolderOnlyInNavtree', False)
        topLevel = calculateTopLevel(context, portlet, context.REQUEST)

        self.rootPath = getRootPath(
            context,
            currentFolderOnly,
            topLevel,
            portlet.root)


class CPSkinRenderer(Renderer):
    _template = ViewPageTemplateFile('navigation.pt')
    recurse = ViewPageTemplateFile('navigation_recurse.pt')

    @memoize
    def getNavRootPath(self):
        currentFolderOnly = self.data.currentFolderOnly or \
            self.properties.getProperty('currentFolderOnlyInNavtree', False)

        topLevel = calculateTopLevel(self.context, self.data, self.request)
        root = self.data.root
        if isinstance(root, unicode):
            root = str(root)

        return getRootPath(self.context, currentFolderOnly, topLevel, root)

    def createNavTree(self):
        data = self.getNavTree()
        for item in data.get('children'):
            if item.get('portal_type') == 'Link':
                current_user = api.user.get_current()
                obj_link = item.get('item').getObject()
                can_edit = current_user.has_permission('Edit', obj_link)
                item['target_blank'] = '_blank' if getattr(obj_link, 'target_blank', False) and not can_edit else '_self'
        bottomLevel = self.data.bottomLevel or 0

        if bottomLevel < 0:
            # Special case where navigation tree depth is negative
            # meaning that the admin does not want the listing to be displayed
            return self.recurse([], level=1, bottomLevel=bottomLevel)
        else:
            return self.recurse(children=data.get('children', []), level=1, bottomLevel=bottomLevel)
