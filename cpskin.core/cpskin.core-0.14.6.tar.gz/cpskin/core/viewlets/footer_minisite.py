# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from cpskin.minisite.interfaces import IInMinisiteBase
from cpskin.minisite.utils import get_minisite_object
from plone import api
from plone.app.layout.viewlets.common import ViewletBase


class CPSkinFooterMinisiteViewlet(ViewletBase):
    render = ViewPageTemplateFile('footer_minisite.pt')

    def available(self):
        request = self.request
        if not IInMinisiteBase.providedBy(request):
            return False
        content = self.content()
        if content is None:
            return False
        elif api.content.get_state(obj=content) != 'published_and_hidden':
            return False
        return True

    def content(self):
        request = self.request
        minisite_obj = get_minisite_object(request)
        document = getattr(minisite_obj, 'footer-mini-site', None)
        return document
