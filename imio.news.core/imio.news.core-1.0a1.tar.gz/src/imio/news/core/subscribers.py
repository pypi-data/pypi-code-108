# -*- coding: utf-8 -*-

from imio.news.core.utils import get_entity_for_obj
from imio.news.core.utils import get_news_folder_for_news_item
from imio.news.core.utils import reload_faceted_config
from plone import api
from zope.globalrequest import getRequest
from zope.lifecycleevent import ObjectRemovedEvent
from zope.lifecycleevent.interfaces import IAttributes


def set_default_news_folder_uid(news_item):
    news_item.selected_news_folders = news_item.selected_news_folders or []
    uid = get_news_folder_for_news_item(news_item).UID()
    if uid not in news_item.selected_news_folders:
        news_item.selected_news_folders = news_item.selected_news_folders + [uid]
        news_item.reindexObject(idxs=["selected_news_folders"])


def added_entity(obj, event):
    request = getRequest()
    reload_faceted_config(obj, request)


def added_news_folder(obj, event):
    request = getRequest()
    reload_faceted_config(obj, request)
    entity = get_entity_for_obj(obj)
    reload_faceted_config(entity, request)


def modified_newsfolder(obj, event):
    mark_current_newsfolder_in_news_from_other_newsfolder(obj, event)


def removed_newsfolder(obj, event):
    try:
        brains = api.content.find(selected_news_folders=obj.UID())
    except api.exc.CannotGetPortalError:
        # This happen when we try to remove plone object
        return
    for brain in brains:
        news = brain.getObject()
        news.selected_news_folders = [
            uid for uid in news.selected_news_folders if uid != obj.UID()
        ]
        news.reindexObject(idxs=["selected_news_folders"])
    request = getRequest()
    entity = get_entity_for_obj(obj)
    reload_faceted_config(entity, request)


def added_news_item(obj, event):
    container_newsfolder = get_news_folder_for_news_item(obj)
    set_uid_of_referrer_newsfolders(obj, event, container_newsfolder)


def modified_news_item(obj, event):
    set_default_news_folder_uid(obj)


def moved_news_item(obj, event):
    if event.oldParent == event.newParent and event.oldName != event.newName:
        # item was simply renamed
        return
    if type(event) is ObjectRemovedEvent:
        # We don't have anything to do if news item is being removed
        return
    container_newsfolder = get_news_folder_for_news_item(obj)
    set_uid_of_referrer_newsfolders(obj, event, container_newsfolder)


def mark_current_newsfolder_in_news_from_other_newsfolder(obj, event):
    changed = False
    newsfolders_to_treat = []
    for d in event.descriptions:
        if not IAttributes.providedBy(d):
            # we do not have fields change description, but maybe a request
            continue
        if "populating_newsfolders" in d.attributes:
            changed = True
            uids_in_current_newsfolder = [
                rf.to_object.UID() for rf in obj.populating_newsfolders
            ]
            old_uids = getattr(obj, "old_populating_newsfolders", [])
            newsfolders_to_treat = set(old_uids) ^ set(uids_in_current_newsfolder)
            break
    if not changed:
        return
    for uid_newsfolder in newsfolders_to_treat:
        newsfolder = api.content.get(UID=uid_newsfolder)
        news_brains = api.content.find(
            context=newsfolder, portal_type="imio.news.NewsItem"
        )
        for brain in news_brains:
            news = brain.getObject()
            if uid_newsfolder in uids_in_current_newsfolder:
                news.selected_news_folders.append(obj.UID())
            else:
                news.selected_news_folders = [
                    item for item in news.selected_news_folders if item != obj.UID()
                ]
            news.reindexObject(idxs=["selected_news_folders"])
    # Keep a copy of populating_newsfolders
    obj.old_populating_newsfolders = uids_in_current_newsfolder


def set_uid_of_referrer_newsfolders(obj, event, container_newsfolder):
    obj.selected_news_folders = [container_newsfolder.UID()]
    rels = api.relation.get(
        target=container_newsfolder, relationship="populating_newsfolders"
    )
    if not rels:
        return
    for rel in rels:
        obj.selected_news_folders.append(rel.from_object.UID())
    obj.reindexObject(idxs=["selected_news_folders"])
