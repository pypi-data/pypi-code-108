# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from collective.taxonomy import PATH_SEPARATOR
from collective.taxonomy.interfaces import ITaxonomy
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema import getFields
from zope.schema.interfaces import IVocabularyFactory


class CommonView(BrowserView):

    def translate_taxonomy(self, msgid, domain=''):
        sm = getSiteManager()
        utility = sm.queryUtility(ITaxonomy, name=domain)
        target_language = str(utility.getCurrentLanguage(self.request))
        if msgid not in utility.inverted_data[target_language]:
            return ''
        path = utility.inverted_data[target_language][msgid]
        sub_category = path[1:].split(PATH_SEPARATOR)[-1]
        return sub_category

    def see_categories(self, container):
        result = True
        taxonomy_field = getattr(container, 'taxonomy_category', '')
        if not taxonomy_field:
            result = False
        return result

    def get_field_taxonomy(self, obj, field, taxonomy_field, limit=None):
        vocabulary_name = field.value_type.vocabularyName
        factory = getUtility(IVocabularyFactory, vocabulary_name)
        vocabulary = factory(api.portal.get())
        tokens = getattr(obj, taxonomy_field, '')
        if not tokens:
            return ''
        categories = []
        for token in tokens:
            cat = vocabulary.inv_data.get(token)
            if not cat:
                return ''
            # format is "/taxlevel1/taxlevel2/..." and we want the last term
            last_term = cat.split(PATH_SEPARATOR)[-1]
            categories.append(last_term)
        if limit is None:
            categories.sort()
        else:
            categories = categories[:limit]
        return ', '.join(categories)

    def get_behavior_taxonomy(self, obj, short_name, limit=None):
        categories = []
        if not getattr(obj, 'taxonomy_' + short_name, None):
            return ''
        for taxon in getattr(obj, 'taxonomy_' + short_name):
            categories.append(self.translate_taxonomy(
                taxon,
                domain='collective.taxonomy.' + short_name
            ))
        if limit is None:
            categories.sort()
        else:
            categories = categories[:limit]
        return ', '.join(categories)

    def get_categories(self, container, obj, limit=None):
        portal_type = obj.portal_type
        schema = getUtility(IDexterityFTI, name=portal_type).lookupSchema()
        fields = getFields(schema)
        taxonomy_field = getattr(container, 'taxonomy_category', '')
        if not taxonomy_field:
            return
        if taxonomy_field in fields.keys():
            field = fields[taxonomy_field]
            return self.get_field_taxonomy(obj, field, taxonomy_field, limit)

        long_name = 'collective.taxonomy.{0}'.format(
            taxonomy_field.replace('taxonomy_', '').replace('_', ''))
        utility = queryUtility(ITaxonomy, long_name)
        if utility is not None:
            short_name = utility.getShortName()
            return self.get_behavior_taxonomy(obj, short_name, limit)

        return ''
