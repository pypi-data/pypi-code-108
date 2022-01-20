# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import common
from plone.registry.interfaces import IRegistry
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from sc.social.like.browser.viewlets import SocialLikesViewlet as SLV
from zope.component import getUtility

import operator


class SocialViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('social.pt')

    def getSocialLinks(self):
        registry = getUtility(IRegistry)
        links_dict = registry['cpskin.core.socialviewlet']
        links_ordered = sorted(links_dict.itervalues(), key=operator.itemgetter(0))
        # Fix bad encoded cpskin.core.socialviewlet registry :
        links_ordered = [li for li in links_ordered if len(li) == 3]
        return links_ordered


class SocialLikesViewlet(SLV):
    def enabled(self):
        """Check if the viewlet should be visible on this context."""
        allowed_states = api.portal.get_registry_record(
            'cpskin.core.social.allowed_states',
            default=['published_and_shown', 'published_and_hidden'],
        )
        try:
            published = api.content.get_state(self.context) in allowed_states
        except WorkflowException:
            # no workflow on context, like in site root
            published = True
        return all([published, self.helper.enabled(), self.plugins()])
