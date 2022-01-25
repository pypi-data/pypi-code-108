# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Acquisition import aq_parent
from imio.news.core.contents import IEntity
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory


class NewsCategoriesVocabularyFactory:
    def __call__(self, context=None):
        values = [
            (u"job_offer", _(u"Job offer")),
            (u"presse", _(u"Presse")),
            (u"city_project", _(u"City project")),
            (u"works", _(u"Works")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


NewsCategoriesVocabulary = NewsCategoriesVocabularyFactory()


class NewsLocalCategoriesVocabularyFactory:
    def __call__(self, context=None):
        if IPloneSiteRoot.providedBy(context):
            # ex: call on @types or @vocabularies from RESTAPI
            return SimpleVocabulary([])
        obj = context
        while not IEntity.providedBy(obj):
            obj = aq_parent(aq_inner(obj))
        if not obj.local_categories:
            return SimpleVocabulary([])

        values = obj.local_categories.splitlines()
        terms = [SimpleTerm(value=t, token=t, title=t) for t in values]
        return SimpleVocabulary(terms)


NewsLocalCategoriesVocabulary = NewsLocalCategoriesVocabularyFactory()


class NewsCategoriesAndTopicsVocabularyFactory:
    def __call__(self, context=None):
        news_categories_factory = getUtility(
            IVocabularyFactory, "imio.news.vocabulary.NewsCategories"
        )

        news_local_categories_factory = getUtility(
            IVocabularyFactory, "imio.news.vocabulary.NewsLocalCategories"
        )

        topics_factory = getUtility(
            IVocabularyFactory, "imio.smartweb.vocabulary.Topics"
        )

        terms = []

        for term in news_categories_factory(context):
            terms.append(
                SimpleTerm(
                    value=term.value,
                    token=term.token,
                    title=term.title,
                )
            )

        for term in news_local_categories_factory(context):
            terms.append(
                SimpleTerm(
                    value=term.value,
                    token=term.token,
                    title=term.title,
                )
            )

        for term in topics_factory(context):
            terms.append(
                SimpleTerm(
                    value=term.value,
                    token=term.token,
                    title=term.title,
                )
            )
        return SimpleVocabulary(terms)


NewsCategoriesAndTopicsVocabulary = NewsCategoriesAndTopicsVocabularyFactory()


class NewsFoldersUIDsVocabularyFactory:
    def __call__(self, context=None):
        portal = api.portal.get()
        brains = api.content.find(
            context=portal,
            portal_type="imio.news.NewsFolder",
            sort_on="sortable_title",
        )
        terms = [
            SimpleTerm(value=b.UID, token=b.UID, title=b.breadcrumb) for b in brains
        ]
        return SimpleVocabulary(terms)


NewsFoldersUIDsVocabulary = NewsFoldersUIDsVocabularyFactory()
