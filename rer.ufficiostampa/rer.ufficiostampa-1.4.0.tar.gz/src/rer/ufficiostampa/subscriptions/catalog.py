# -*- coding: utf-8 -*-
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from souper.interfaces import ICatalogFactory
from souper.soup import NodeAttributeIndexer
from zope.interface import implementer
from repoze.catalog.indexes.text import CatalogTextIndex
from souper.soup import NodeTextIndexer
from repoze.catalog.indexes.keyword import CatalogKeywordIndex

import logging

logger = logging.getLogger(__name__)


@implementer(ICatalogFactory)
class SubscriptionsSoupCatalogFactory(object):
    def __call__(self, context):
        catalog = Catalog()
        text_indexer = NodeTextIndexer(["name", "surname", "email"])
        catalog[u"text"] = CatalogTextIndex(text_indexer)
        email_indexer = NodeAttributeIndexer("email")
        catalog[u"email"] = CatalogFieldIndex(email_indexer)
        name_indexer = NodeAttributeIndexer("name")
        catalog[u"name"] = CatalogFieldIndex(name_indexer)
        surname_indexer = NodeAttributeIndexer("surname")
        catalog[u"surname"] = CatalogFieldIndex(surname_indexer)
        channels_indexer = NodeAttributeIndexer("channels")
        catalog[u"channels"] = CatalogKeywordIndex(channels_indexer)
        date_indexer = NodeAttributeIndexer("date")
        catalog[u"date"] = CatalogFieldIndex(date_indexer)
        newspaper_indexer = NodeAttributeIndexer("newspaper")
        catalog[u"newspaper"] = CatalogFieldIndex(newspaper_indexer)
        return catalog


@implementer(ICatalogFactory)
class SendHistorySoupCatalogFactory(object):
    def __call__(self, context):
        catalog = Catalog()
        channels_indexer = NodeAttributeIndexer("channels")
        catalog[u"channels"] = CatalogKeywordIndex(channels_indexer)
        date_indexer = NodeAttributeIndexer("date")
        catalog[u"date"] = CatalogFieldIndex(date_indexer)
        title_indexer = NodeAttributeIndexer("title")
        catalog[u"title"] = CatalogTextIndex(title_indexer)
        type_indexer = NodeAttributeIndexer("type")
        catalog[u"type"] = CatalogFieldIndex(type_indexer)
        return catalog
