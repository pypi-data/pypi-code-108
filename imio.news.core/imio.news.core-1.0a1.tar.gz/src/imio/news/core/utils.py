# -*- coding: utf-8 -*-

from eea.facetednavigation.settings.interfaces import IHidePloneLeftColumn
from imio.news.core.contents import IEntity
from imio.news.core.contents import INewsFolder
from imio.smartweb.common.faceted.utils import configure_faceted
from plone import api
from Products.CMFPlone.utils import parent
from zope.component import getMultiAdapter
from zope.interface import noLongerProvides

import os


def get_entity_for_obj(obj):
    while not IEntity.providedBy(obj):
        obj = parent(obj)
    entity = obj
    return entity


def get_news_folder_for_news_item(news_item):
    obj = news_item
    while not INewsFolder.providedBy(obj):
        obj = parent(obj)
    news_folder = obj
    return news_folder


def get_news_folders_uids_for_faceted(obj):
    if INewsFolder.providedBy(obj):
        return [obj.UID()]
    elif IEntity.providedBy(obj):
        brains = api.content.find(context=obj, portal_type="imio.news.NewsFolder")
        return [b.UID for b in brains]
    else:
        raise NotImplementedError


def reload_faceted_config(obj, request):
    faceted_config_path = "{}/faceted/config/news.xml".format(os.path.dirname(__file__))
    configure_faceted(obj, faceted_config_path)
    news_folders_uids = "\n".join(get_news_folders_uids_for_faceted(obj))
    request.form = {
        "cid": "newsfolders",
        "faceted.newsfolders.default": news_folders_uids,
    }
    handler = getMultiAdapter((obj, request), name=u"faceted_update_criterion")
    handler.edit(**request.form)
    if IHidePloneLeftColumn.providedBy(obj):
        noLongerProvides(obj, IHidePloneLeftColumn)
