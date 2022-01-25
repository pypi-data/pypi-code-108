# -*- coding: utf-8 -*-
from imio.gdpr import DEFAULT_COOKIES_FILES
from imio.gdpr import DEFAULT_GDPR_FILES
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class DefaultGDPRPage(BrowserView):

    index = ViewPageTemplateFile('default_gdpr_text.pt')


class DefaultCookiesPage(BrowserView):

    index = ViewPageTemplateFile('default_cookies_text.pt')


class BaseView(BrowserView):

    index = ViewPageTemplateFile('view.pt')
    default_filenames = []
    text_record = ""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        nav_root = api.portal.get_navigation_root(self.context)
        for name in self.default_filenames:
            content = getattr(nav_root, name, None)
            if content and content.Language() == self.context.Language():
                return self.request.response.redirect(content.absolute_url())
        return self.index()

    def content(self):
        text = api.portal.get_registry_record(self.text_record, default='')
        return text


class GDPRView(BaseView):

    default_filenames = DEFAULT_GDPR_FILES
    text_record = "imio.gdpr.interfaces.IGDPRSettings.text"


class CookiesView(BaseView):

    default_filenames = DEFAULT_COOKIES_FILES
    text_record = "imio.gdpr.interfaces.IGDPRSettings.cookies_text"
