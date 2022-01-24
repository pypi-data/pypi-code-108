# -*- coding: utf-8 -*-
from plone import api
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class IPhotoPortlet(IPortletDataProvider):
    """
    Photo portlet interface
    """


class Assignment(base.Assignment):
    implements(IPhotoPortlet)


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('photo.pt')

    @property
    def available(self):
        """
        Portlet should be available from the 3 level of navigation
        """
        contextPhyPath = self.context.getPhysicalPath()
        portalPhyPath = api.portal.get().getPhysicalPath()
        path = [elem for elem in list(contextPhyPath) if elem not in list(portalPhyPath)]  # noqa
        depth = len(path)
        if depth < 2:
            return False
        return True

    def get_visuel(self):
        visuel = getattr(self.context, 'visuel.png', None)
        if visuel is not None:
            visuel = visuel.aq_inner
            return visuel.absolute_url()
        return ''


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
