# -*- coding: utf-8 -*-

from imio.events.core.contents.event.content import IEvent
from imio.events.core.utils import get_agenda_for_event
from imio.smartweb.common.utils import translate_vocabulary_term
from plone.indexer import indexer
from plone import api
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.contenttypes.indexers import _unicode_save_string_concat
from plone.app.textfield.value import IRichTextValue
from Products.CMFPlone.utils import safe_unicode

import copy


@indexer(IEvent)
def category_title(obj):
    if obj.category is not None:
        return translate_vocabulary_term(
            "imio.events.vocabulary.EventsCategories", obj.category
        )


@indexer(IEvent)
def category_and_topics_indexer(obj):
    values = []
    if obj.topics is not None:
        values = copy.deepcopy(obj.topics)

    if obj.category is not None:
        values.append(obj.category)

    if obj.local_category is not None:
        values.append(obj.local_category)

    return values


@indexer(IEvent)
def container_uid(obj):
    uid = get_agenda_for_event(obj).UID()
    return uid


@indexer(IEvent)
def SearchableText_event(obj):
    text = ""
    textvalue = IRichText(obj).text
    if IRichTextValue.providedBy(textvalue):
        transforms = api.portal.get_tool("portal_transforms")
        raw = safe_unicode(textvalue.raw)
        text = (
            transforms.convertTo(
                "text/plain",
                raw,
                mimetype=textvalue.mimeType,
            )
            .getData()
            .strip()
        )

    topics = []
    for topic in getattr(obj.aq_base, "topics", []) or []:
        topics.append(
            translate_vocabulary_term("imio.smartweb.vocabulary.Topics", topic)
        )

    category = translate_vocabulary_term(
        "imio.events.vocabulary.EventsCategories",
        getattr(obj.aq_base, "category", None),
    )

    result = " ".join(
        (
            safe_unicode(obj.title) or "",
            safe_unicode(obj.description) or "",
            safe_unicode(text),
            *topics,
            safe_unicode(category),
        )
    )
    return _unicode_save_string_concat(result)
