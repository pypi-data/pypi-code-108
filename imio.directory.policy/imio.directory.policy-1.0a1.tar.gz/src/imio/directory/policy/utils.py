# -*- coding: utf-8 -*-

from plone import api


def remove_unused_contents(portal):
    api.content.delete(portal.news)
    api.content.delete(portal.events)
    api.content.delete(portal.Members)
