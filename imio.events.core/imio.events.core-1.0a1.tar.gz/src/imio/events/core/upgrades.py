# -*- coding: utf-8 -*-

from imio.events.core.utils import reload_faceted_config
from plone import api
from zope.globalrequest import getRequest

import logging

logger = logging.getLogger("imio.events.core")


def refresh_objects_faceted(context):
    request = getRequest()
    brains = api.content.find(portal_type=["imio.events.Entity", "imio.events.Agenda"])
    for brain in brains:
        obj = brain.getObject()
        reload_faceted_config(obj, request)
        logger.info("Faceted refreshed on {}".format(obj.Title()))
