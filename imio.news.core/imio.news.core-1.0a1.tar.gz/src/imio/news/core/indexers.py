# -*- coding: utf-8 -*-

from imio.news.core.contents.newsitem.content import INewsItem
from imio.news.core.utils import get_news_folder_for_news_item
from imio.smartweb.common.utils import translate_vocabulary_term
from plone import api
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.contenttypes.indexers import _unicode_save_string_concat
from plone.app.textfield.value import IRichTextValue
from plone.indexer import indexer
from Products.CMFPlone.utils import safe_unicode

import copy


@indexer(INewsItem)
def category_title(obj):
    if obj.category is not None:
        return translate_vocabulary_term(
            "imio.news.vocabulary.NewsCategories", obj.category
        )


@indexer(INewsItem)
def category_and_topics_indexer(obj):
    list = []
    if obj.topics is not None:
        list = copy.deepcopy(obj.topics)

    if obj.category is not None:
        list.append(obj.category)

    if obj.local_categories is not None:
        list.append(obj.local_category)
    return list


@indexer(INewsItem)
def container_uid(obj):
    uid = get_news_folder_for_news_item(obj).UID()
    return uid


@indexer(INewsItem)
def SearchableText_news_item(obj):
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
        "imio.news.vocabulary.NewsCategories", getattr(obj.aq_base, "category", None)
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
