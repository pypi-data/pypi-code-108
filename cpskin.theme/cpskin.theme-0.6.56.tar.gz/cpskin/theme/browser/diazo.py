# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.theming.utils import getCurrentTheme
from plone.dexterity.interfaces import IDexterityContent
from plone.outputfilters.filters.resolveuid_and_caption import ResolveUIDAndCaptionFilter  # noqa
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
HAS_MINISITE = False
try:
    from cpskin.minisite.browser.interfaces import IHNavigationActivated
    from cpskin.minisite.interfaces import IInMinisite
    from cpskin.minisite.interfaces import IInPortal
    from cpskin.minisite.utils import get_minisite_object
    HAS_MINISITE = True
except ImportError:
    pass


import os


class DiazoView(BrowserView):

    def isInMinisite(self):
        if not HAS_MINISITE:
            return False
        return (self.isInMinisiteMode() or self.isInPortalMode())

    def isInMinisiteMode(self):
        """
        Returns true if we are in minisite mode
        """
        if not HAS_MINISITE:
            return False
        request = self.request
        return IInMinisite.providedBy(request)

    def isInPortalMode(self):
        if not HAS_MINISITE:
            return False
        request = self.request
        return IInPortal.providedBy(request)

    def withMinisiteHorizontalNav(self):
        if not HAS_MINISITE:
            return False
        if not self.isInMinisiteMode():
            return False
        request = self.request
        minisite_root = get_minisite_object(request)
        return IHNavigationActivated.providedBy(minisite_root)

    def horizontalNavActivated(self):
        if not HAS_MINISITE:
            return False
        if not self.isInMinisite():
            return False
        request = self.request
        minisite_root = get_minisite_object(request)
        return IHNavigationActivated.providedBy(minisite_root)

    def getCurrentTheme(self):
        return getCurrentTheme()

    def is_homepage(self):
        """
        Returns true if we are on navigation root
        """
        obj = aq_inner(self.context)
        if INavigationRoot.providedBy(obj):
            return True
        return False

    def is_folder_view(self):
        """
        Returns true if we are on an index view
        """
        context = self.context
        if IDexterityContent.providedBy(self.context):
            layout = context.getLayout()
            return (layout == 'folderview')
        else:
            return False

    def get_environment(self):
        """
        Get value of ENV environment variable.
        Value should be : dev, staging, preprod or prod.
        """
        env = os.getenv('ENV', 'prod')
        return env.lower()

    def search_position(self):
        return api.portal.get_registry_record(
            'cpskin.core.interfaces.ICPSkinSettings.search_position')

    def is_search_in_banner(self):
        context = self.context
        banner_view = getMultiAdapter((context, self.request),
                                      name='banner_activation')
        if not banner_view.is_enabled:
            return False
        return self.search_position() == 'default_position'

    def is_search_in_navigation(self):
        if self.search_position() == 'always_in_navigation':
            return True
        elif self.search_position() == 'default_position':
            return not(self.is_search_in_banner())
        return False

    def is_search_in_actions(self):
        return self.search_position() == 'always_in_actions'

    def get_login_message(self):
        nav_root = api.portal.get_navigation_root(self.context)
        login_message_page = getattr(nav_root, 'login-message', None)
        if not login_message_page or not login_message_page.text:
            return u''

        login_message = login_message_page.text.raw
        login_message = login_message.replace(
            'http://resolveuid/', 'resolveuid/')
        parser = ResolveUIDAndCaptionFilter(login_message_page)
        transform_text = parser(login_message)
        # return login_message_page.absolute_url()
        return transform_text
