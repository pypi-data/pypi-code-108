# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Intelligent search functionality.

Requires ElasticSearch to be installed.

See :doc:`/plugins/search`.
"""

import os
import subprocess
from pathlib import Path

from django.conf import settings

from lino.api import ad
from lino.core.site import has_elasticsearch, has_haystack

class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    # needs_plugins = ['lino.modlib.restful']

    # ES_url = 'localhost:9200' # running a docker instance locally
    ES_url = 'https://elastic:mMh6KlFP0UAooywwsWPLJ3ae@lino.es.us-central1.gcp.cloud.es.io:9243'
    """URL to the elasticsearch instance"""

    # Append '/collection_name' at the end of the url when connecting with a
    # collection cluster
    SolrUrl = '{scheme}://{host_name}:{port}/solr'.format(
        scheme = 'http',
        host_name = 'localhost',
        port = '8983'
    )

    mappings_dir = Path(__file__).parent / 'search/mappings'

    debian_dev_server = False

    DEFAULT_ES_INDEX_SETTINGS = {
        'settings': {
            'analysis': {
                'analyzer': {
                    'autocomplete': {
                        'tokenizer': 'autocomplete',
                        'filter': ['lowercase']
                    },
                    'autocomplete_search': {
                        'tokenizer': 'lowercase'
                    },
                    'index_analyzer': {
                        'tokenizer': 'autocomplete',
                        'filter': ['lowercase']
                    }
                },
                'tokenizer': {
                    'autocomplete': {
                        'type': 'edge_ngram',
                        'min_gram': 2,
                        'max_gram': 20,
                        'token_chars': ['letter', 'digit', 'punctuation'],
                        'custom_token_chars': '#+-_'
                    }
                }
            }
        }
    }

    def on_init(self):
        super().on_init()

        if self.site.use_solr and has_haystack:
            self.needs_plugins.append('haystack')
            haystack_solr_connections = {
                'default': {
                    'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
                    'URL': self.SolrUrl + '/lino',
                    'ADMIN_URL': self.SolrUrl + '/admin/cores',
                    'TIMEOUT': 60,
                    'INCLUDE_SPELLING': True,
                    'BATCH_SIZE': 1000
                }
            }
            settings.HAYSTACK_CONNECTIONS = haystack_solr_connections
            settings.HAYSTACK_DOCUMENT_FIELD = 'search_doc'
            haystack_solr_settings = {
                'HAYSTACK_CONNECTIONS': settings.HAYSTACK_CONNECTIONS,
                'HAYSTACK_DOCUMENT_FIELD': settings.HAYSTACK_DOCUMENT_FIELD,
                'HAYSTACK_SIGNAL_PROCESSOR': 'haystack.signals.RealtimeSignalProcessor',
                'HAYSTACK_LIMIT_TO_REGISTERED_MODELS': True,
                'HAYSTACK_SEARCH_RESULTS_PER_PAGE': 15,
                'HAYSTACK_ITERATOR_LOAD_PER_QUERY': 15,
                'HAYSTACK_CURRENCY_FIELD_OPENEXCHANGERATES_APP_ID': '374284e075f348e7bff99e566d3202a7'
            }
            self.site.update_settings(**haystack_solr_settings)

        if self.site.use_elasticsearch and has_elasticsearch:
            from lino.modlib.search.utils import ESResolver
            self.needs_plugins.append('elasticsearch_django')

            sarset = {
                'connections': {
                    'default': self.ES_url,
                },
                'indexes': ESResolver.read_indexes(),
                'settings': {
                    'chunk_size': 500,
                    'page_size': 15,
                    'auto_sync': True,
                    'strict_validation': False,
                    'mappings_dir': self.mappings_dir,
                    'never_auto_sync': [],
                }
            }
            self.site.update_settings(SEARCH_SETTINGS=sarset)

    def get_requirements(self, site):
        if site.use_elasticsearch:
            yield 'elasticsearch-django'
        if site.use_solr:
            yield 'pysolr'
            yield 'django-haystack'
        # else:
        #     return []

    def get_quicklinks(self):
        if has_elasticsearch and self.site.use_elasticsearch:
            yield 'search.ElasticSiteSearch'
        elif has_haystack and self.site.use_solr:
            yield 'search.SolrSiteSearch'
        else:
            yield 'search.SiteSearch'
