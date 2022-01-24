# -*- coding: utf-8 -*-
from cpskin.core.menu.interfaces import IConfigurationsMenu
from cpskin.core.menu.interfaces import IConfigurationsSubMenuItem
from cpskin.locales import CPSkinMessageFactory as _
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from zope.browsermenu.menu import BrowserMenu
from zope.browsermenu.menu import BrowserSubMenuItem
from zope.component import getMultiAdapter
from zope.interface import implements


class ConfigurationsSubMenuItem(BrowserSubMenuItem):
    implements(IConfigurationsSubMenuItem)

    title = _(u'label_cpskin_configurations_menu', default=u'Configurations')
    description = _(
        u'title_cpskin_actions_menu',
        default=u'Configurations for the current content item')
    submenuId = 'plone_contentmenu_cpskin_configurations'

    order = 15
    extra = {'id': 'plone-contentmenu-cpskin-configurations'}

    @property
    def action(self):
        return self.context.absolute_url()

    @memoize
    def available(self):
        actions_tool = getToolByName(self.context, 'portal_actions')
        actions = actions_tool.listActionInfos(
            object=self.context,
            categories=('cpskin_configurations',), max=1)
        return len(actions) > 0

    def selected(self):
        return False


class ConfigurationsMenu(BrowserMenu):
    implements(IConfigurationsMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        context_state = getMultiAdapter(
            (context, request),
            name='plone_context_state')
        actions = context_state.actions('cpskin_configurations')
        if not actions:
            return results
        for action in actions:
            if action['allowed']:
                aid = action['id']

                results.append({
                    'title': action['title'],
                    'description': '',
                    'action': action['url'],
                    'selected': False,
                    'icon': None,
                    'extra': {'id': 'plone-contentmenu-cpskin-configurations-' + aid,  # noqa
                              'separator': None,
                              'class': None},
                    'submenu': None,
                })
        return results
