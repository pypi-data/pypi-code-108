# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.navigationtoggle.interfaces import INavigationToggleSettings
from cpskin.core.browser.interfaces import INavigationToggleView
from cpskin.locales import CPSkinMessageFactory as _
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IFolderish
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements


class NavigationToggleView(BrowserView):
    """Navigation toggle activation helper view"""
    implements(INavigationToggleView)

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

    def relative_path(self, obj):
        portal_url = api.portal.get().absolute_url()
        relative_path = obj.absolute_url().replace(portal_url, '')
        if not relative_path.startswith('/'):
            relative_path = '/%s' % relative_path
        return unicode(relative_path)

    @property
    def settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationToggleSettings, check=False)
        return settings

    @property
    def is_enabled(self):
        context = self._get_real_context()
        if not IFolderish.providedBy(context):
            return False
        context = self._get_real_context()
        return self.relative_path(context) in self.settings.selectors

    @property
    def can_enable_navigation_toggle(self):
        context = self._get_real_context()
        if not IFolderish.providedBy(context):
            return False
        return not self.is_enabled

    @property
    def can_disable_navigation_toggle(self):
        return self.is_enabled

    def enable_navigation_toggle(self):
        """Enable the navigation toggle on folder"""
        context = self._get_real_context()
        current_paths = self.settings.selectors
        current_paths_list = list(current_paths)
        current_paths_list.append(self.relative_path(context))
        self.settings.selectors = tuple(current_paths_list)
        portal_js = api.portal.get_tool('portal_javascripts')
        portal_js.cookResources()
        self._redirect(_(u'Navigation toggle enabled for folder'))

    def disable_navigation_toggle(self):
        """Disable the navigation toggle on folder"""
        context = self._get_real_context()
        current_paths = self.settings.selectors
        current_paths_list = list(current_paths)
        current_paths_list.remove(self.relative_path(context))
        self.settings.selectors = tuple(current_paths_list)
        portal_js = api.portal.get_tool('portal_javascripts')
        portal_js.cookResources()
        self._redirect(_(u'Navigation toggle disabled for folder'))
