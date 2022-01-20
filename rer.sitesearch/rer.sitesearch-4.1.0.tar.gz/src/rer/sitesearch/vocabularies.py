# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from Products.CMFCore.utils import getToolByName
from rer.sitesearch.interfaces import ISiteSearchCustomFilters
from rer.sitesearch.utils import GROUP_ICONS
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite

try:
    from rer.solrpush.interfaces.settings import IRerSolrpushSettings

    HAS_SOLR = True
except ImportError:
    HAS_SOLR = False


@implementer(IVocabularyFactory)
class IndexesVocabulary(object):
    """
    Vocabulary factory for allowable indexes in catalog.
    """

    def __call__(self, context):
        site = getSite()
        pc = getToolByName(site, "portal_catalog")
        indexes = list(pc.indexes())
        indexes.sort()
        indexes = [SimpleTerm(i, i, i) for i in indexes]
        return SimpleVocabulary(indexes)


@implementer(IVocabularyFactory)
class AdvancedFiltersVocabulary(object):
    """
    Vocabulary factory for list of advanced filters
    """

    def __call__(self, context):

        sm = getGlobalSiteManager()
        request = getRequest()
        adapters = [
            {
                "name": x.name,
                "label": translate(x.factory.label, context=request),
            }
            for x in sm.registeredAdapters()
            if x.provided == ISiteSearchCustomFilters
        ]
        terms = [
            SimpleTerm(
                value=i["name"],
                token=i["name"],
                title=i["label"],
            )
            for i in sorted(adapters, key=lambda i: i["label"])
        ]
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class GroupIconsVocabulary(object):
    """
    Vocabulary factory for list of available icons
    """

    def __call__(self, context):
        request = getRequest()
        terms = [
            SimpleTerm(
                value=i["id"],
                token=i["id"],
                title=translate(i["label"], context=request),
            )
            for i in GROUP_ICONS
        ]
        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class GroupingTypesVocabulary(object):
    """ """

    def __call__(self, context):
        voc_id = "plone.app.vocabularies.ReallyUserFriendlyTypes"
        if HAS_SOLR:
            try:
                if api.portal.get_registry_record(
                    "active", interface=IRerSolrpushSettings
                ):
                    voc_id = "rer.solrpush.vocabularies.AvailablePortalTypes"
            except (KeyError, InvalidParameterError):
                pass
        factory = getUtility(IVocabularyFactory, voc_id)
        return factory(context)


AdvancedFiltersVocabularyFactory = AdvancedFiltersVocabulary()
GroupingTypesVocabularyFactory = GroupingTypesVocabulary()
GroupIconsVocabularyFactory = GroupIconsVocabulary()
IndexesVocabularyFactory = IndexesVocabulary()
