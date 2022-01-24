# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.conf import settings
from django.db import models

from lino.api import dd, rt, _
from lino.core.site import has_haystack, get_models

if has_haystack and settings.SITE.use_solr:
    from haystack import indexes

def get_SearchIndex_for_model(model):

    class SearchIndex(indexes.SearchIndex, indexes.Indexable):
        document_model_attr = 'edge_ngram_field'
        rendered_field_model_attr = 'haystack_rendered_field'
        search_doc = indexes.EdgeNgramField(document=True)
        rendered = indexes.CharField(indexed=False)

        def get_model(self):
            return model

        def prepare_search_doc(self, object):
            if hasattr(object, self.document_model_attr):
                return getattr(object, self.document_model_attr)
            return ''

        def prepare_rendered(self, object):
            if hasattr(object, self.rendered_field_model_attr):
                return getattr(object, self.rendered_field_model_attr)
            return ''

    return SearchIndex

if has_haystack:
    for model in get_models():
        if model.show_in_site_search:
            locals()[model.__name__ + 'Index'] = get_SearchIndex_for_model(model)
