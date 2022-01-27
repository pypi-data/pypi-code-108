# -*- coding: utf-8 -*-

from imio.smartweb.common.utils import get_vocabulary
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate


def remove_unused_contents(portal):
    api.content.delete(portal.news)
    api.content.delete(portal.events)
    api.content.delete(portal.Members)


def clear_manager_portlets(folder, manager_name):
    manager = getUtility(IPortletManager, name=manager_name, context=folder)
    assignments = getMultiAdapter((folder, manager), IPortletAssignmentMapping)
    for portlet in assignments:
        del assignments[portlet]


def add_iam_folder(context, current_lang):
    i_am_folder = api.content.create(
        container=context,
        type="imio.smartweb.Folder",
        title=translate(_(u"I am"), target_language=current_lang),
    )
    api.content.transition(i_am_folder, "publish")

    i_am_vocabulary = get_vocabulary("imio.smartweb.vocabulary.IAm")
    for term in i_am_vocabulary:
        link = api.content.create(
            container=i_am_folder,
            type="Link",
            title=translate(_(term.title), target_language=current_lang),
        )
        link.remoteUrl = "{0}/@@search?iam={1}".format("${portal_url}", term.token)
        api.content.transition(link, "publish")


def add_ifind_folder(context, current_lang):
    i_find_folder = api.content.create(
        container=context,
        type="imio.smartweb.Folder",
        title=translate(_(u"I find"), target_language=current_lang),
    )
    api.content.transition(i_find_folder, "publish")
    collection = api.content.create(
        container=i_find_folder,
        type="Collection",
        title=translate(
            _(u"Procedures and practical informations"), target_language=current_lang
        ),
    )
    collection.query = [
        {
            "i": "portal_type",
            "o": "plone.app.querystring.operation.selection.any",
            "v": ["imio.smartweb.Procedure"],
        }
    ]
    api.content.transition(collection, "publish")
    request = getRequest()
    request.form = {
        "cid": "page-category",
        "faceted.page-category.index": "taxonomy_procedure_category",
        "faceted.page-category.vocabulary": "collective.taxonomy.procedure_category",
    }
    handler = getMultiAdapter((collection, request), name=u"faceted_update_criterion")
    handler.edit(**request.form)


def add_navigation_links(context):
    current_lang = api.portal.get_current_language()[:2]
    add_iam_folder(context, current_lang)
    add_ifind_folder(context, current_lang)
