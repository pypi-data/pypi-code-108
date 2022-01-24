# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from cpskin.core.browser.interfaces import IBannerActivationView
from cpskin.core.interfaces import IBannerActivated
from cpskin.core.interfaces import ILocalBannerActivated
from cpskin.locales import CPSkinMessageFactory as _
from plone import api
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides


class BannerActivationView(BrowserView):
    """
    Banner activation helper view
    """
    implements(IBannerActivationView)

    def _redirect(self, msg=''):
        if self.request:
            if msg:
                api.portal.show_message(message=msg,
                                        request=self.request,
                                        type='info')
            self.request.response.redirect(self.context.absolute_url())
        return msg

    def _get_real_context(self):
        context = self.context
        plone_view = getMultiAdapter((context, self.request), name="plone")
        if plone_view.isDefaultPageInFolder():
            context = aq_parent(context)
        context = aq_inner(context)
        return context

    @property
    def is_enabled(self):
        context = self._get_real_context()
        return self.banner_root is not None or ILocalBannerActivated.providedBy(context)

    @property
    def banner_root(self):
        context = self._get_real_context()
        portal = api.portal.get()
        obj = context
        while obj != portal:
            if IBannerActivated.providedBy(obj):
                return obj
            obj = aq_parent(obj)
        if IBannerActivated.providedBy(obj):
            return obj
        return None

    @property
    def can_enable_banner(self):
        return not self.is_enabled

    @property
    def can_disable_banner(self):
        context = self._get_real_context()
        return(IBannerActivated.providedBy(context))

    def enable_banner(self):
        """ Enable the banner """
        context = self._get_real_context()
        alsoProvides(context, IBannerActivated)
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context)
        self._redirect(_(u'Banner enabled on content and sub-contents'))

    def disable_banner(self):
        """ Disable the banner """
        context = self._get_real_context()
        noLongerProvides(context, IBannerActivated)
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context)
        self._redirect(_(u'Banner disabled for content and sub-contents'))

    @property
    def can_enable_local_banner(self):
        return not self.can_disable_local_banner

    @property
    def can_disable_local_banner(self):
        context = self._get_real_context()
        return(ILocalBannerActivated.providedBy(context))

    def enable_local_banner(self):
        """ Enable the banner """
        context = self._get_real_context()
        alsoProvides(context, ILocalBannerActivated)
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context)
        self._redirect(_(u'Banner enabled on content'))

    def disable_local_banner(self):
        """ Disable the banner """
        context = self._get_real_context()
        noLongerProvides(context, ILocalBannerActivated)
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context)
        self._redirect(_(u'Banner disabled for content'))
