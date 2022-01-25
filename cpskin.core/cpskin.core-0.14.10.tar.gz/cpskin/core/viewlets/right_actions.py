# -*- coding: utf-8 -*-

from Acquisition import aq_base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets.content import ContentRelatedItems
from zope.component import getMultiAdapter


class RightActionsViewlet(ContentRelatedItems):

    index = ViewPageTemplateFile('right_actions.pt')

    def update(self):
        self.has_toc = self.hasTOC()
        try:
            self.has_related = len(self.related_items()) > 0
        except:
            self.has_related = 0
        self.has_portlets = self.hasPortletsToShow()
        self.has_useful_links = self.has_related or self.has_portlets
        self.available = True

    def showPortletsInRightPanel(self):
        portal_registry = api.portal.get_tool('portal_registry')
        return portal_registry['cpskin.core.interfaces.ICPSkinSettings.show_portlets_in_right_actions_panel']  # noqa

    def hasPortletsToShow(self):
        if not self.showPortletsInRightPanel():
            return False
        plone_view = getMultiAdapter((self.context,
                                      self.request),
                                     name=u'plone'
        )
        return plone_view.have_portlets('plone.rightcolumn')

    def hasTOC(self):
        obj = aq_base(self.context)
        getTableContents = getattr(obj, 'getTableContents', None)
        has_toc = False
        if getTableContents is not None:
            try:
                has_toc = getTableContents()
            except KeyError:
                # schema not updated yet
                has_toc = False
        # handle dexterity-behavior
        toc = getattr(obj, 'table_of_contents', None)
        if toc is not None:
            has_toc = toc
        return has_toc
