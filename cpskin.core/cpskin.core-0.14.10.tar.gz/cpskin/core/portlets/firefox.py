# -*- coding: utf-8 -*-
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class IFirefoxPortlet(IPortletDataProvider):
    """
    Firefox portlet interface
    """


class Assignment(base.Assignment):
    implements(IFirefoxPortlet)


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('firefox.pt')

    @property
    def available(self):
        return 'Firefox' not in self.request.get('HTTP_USER_AGENT', None)


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
