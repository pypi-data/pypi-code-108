# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import sys
from importlib import import_module

from django.conf import settings
from django.db.models import Manager

from lino.api import dd, rt, _
from lino.modlib.restful.serializers import get_serializer_for_model
from lino.core.site import has_elasticsearch

from etgen.html import E, tostring

from .utils import ESResolver

class SearchDocumentMixin:
    pass

class SearchDocumentManagerMixin:
    pass

if has_elasticsearch and settings.SITE.use_elasticsearch:
    from elasticsearch_django.models import SearchDocumentMixin
    from elasticsearch_django.models import SearchDocumentManagerMixin
    from elasticsearch_django.models import execute_search
    from elasticsearch_django.settings import get_client
    from elasticsearch_django.settings import get_setting
    from elasticsearch_dsl import Search
    from elasticsearch_dsl.query import MultiMatch

    from django.core.cache import cache

    search = Search(using=get_client())


class ElasticSearchableManager(SearchDocumentManagerMixin):
    def get_search_queryset(self, index='_all'):
        return self.get_queryset()

    def annotate_and_get(self, pk, sq):
        return self.from_search_query(sq).filter(pk=pk)[0]


class ElasticSearchable(dd.Model, SearchDocumentMixin):

    class Meta:
        abstract = True

    objects = ElasticSearchableManager()

    ES_indexes = [('global', )]
    """Set of elastic search indexes, (when installed)."""

    def as_search_document(self, index):
        serializer = self.build_document(index)
        if serializer is None:
            return {}
        data = serializer(self).data
        data.update(model=self._meta.app_label + '.' + self.__class__.__name__)
        return data

    def build_document(self, index):
        for i in self.ES_indexes:
            if i[0] == index:
                models = ESResolver.get_models_by_index(index)
                if len(models) == 1:
                    assert models[0] == self.__class__
                    return get_serializer_for_model(self.__class__)
                elif len(i) == 1:
                    return get_serializer_for_model(self.__class__)
                else:
                    options = i[1]
                    child = options.get('child', None)
                    if child is not None:
                        child_serializer = get_sesializer_for_model(eval('rt.models.' + child))
                        return get_serializer_for_model(self.__class__, {
                            'extra_fields': {
                                child.split('.')[0].lower() + '_set': child_serializer
                            }
                        })

    @classmethod
    def get_es_example_object(cls, index):
        for i in cls.ES_indexes:
            if len(i) > 1 and i[0] == index and hasattr(i[1], 'example_object'):
                return i[1]['example_object']

        for d in settings.FIXTURE_DIRS:
            if d not in sys.path:
                sys.path.append(d)

        def iter_recursively(obj):
            if hasattr(obj, '__iter__'):
                for o in obj:
                    document = iter_recursively(o)
                    if document is not None:
                        return document
            else:
                if hasattr(obj, 'search_indexes') and index in obj.search_indexes:
                    return obj.as_search_document(index=index)

        def find_from_fixture(fixture):
            try:
                mod = import_module(fixture)
                for obj in mod.objects():
                    document = iter_recursively(obj)
                    if document is not None:
                        return document
            except ModuleNotFoundError:
                pass

        app_fixtures = cls._meta.app_config.name + '.fixtures'

        for module_name in settings.SITE.demo_fixtures:
            found = find_from_fixture(module_name)
            if found is None:
                app_fixture = app_fixtures + '.' + module_name
                found = find_from_fixture(app_fixture)
            if found is not None:
                return found


    def index_search_document(self, *, index: str) -> None:
        """
        Create or replace search document in named index.
        Checks the local cache to see if the document has changed,
        and if not aborts the update, else pushes to ES, and then
        resets the local cache. Cache timeout is set as "cache_expiry"
        in the settings, and defaults to 60s.
        """
        super().index_search_document(index=index)

        if False:
            cache_key = self.search_document_cache_key
            new_doc = self.as_search_document(index=index)
            cached_doc = cache.get(cache_key)
            if new_doc == cached_doc:
                logger.debug("Search document for %r is unchanged, ignoring update.", self)
                return
            cache.set(cache_key, new_doc, timeout=get_setting("cache_expiry", 60))
            try:
                get_client().index(index=index, body=new_doc, id=self.pk)
            except Exception as e:
                dd.logger.error(e.error)
                dd.logger.info(e.info)
