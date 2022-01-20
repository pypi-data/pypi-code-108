# -*- coding: utf-8 -*-
from plone.app.event.browser.event_listing import EventListing as BaseEventListing


class EventListing(BaseEventListing):

    def __call__(self, *args, **kwargs):
        return
