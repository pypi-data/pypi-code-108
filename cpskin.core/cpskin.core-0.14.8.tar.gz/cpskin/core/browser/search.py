# -*- coding: utf-8 -*-
from plone.app.search.browser import Search


class CpskinSearch(Search):

    def filter_query(self, query):
        query = super(CpskinSearch, self).filter_query(query)
        if query is None:
            return {}
        if 'SearchableText' in query.keys():
            searchable_text = query.get('SearchableText', '')
            if searchable_text:
                searchable_text = '{0}*'.format(searchable_text)
                query['SearchableText'] = searchable_text
        return query
