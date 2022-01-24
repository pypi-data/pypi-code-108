# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import logging
logger = logging.getLogger(__name__)
# handler = logging.StreamHandler()
# handler.terminator = ''
# logger.addHandler(handler)

import json
from pathlib import Path

from django.apps import apps
from django.core.management import call_command

try:
    from elasticsearch_django.settings import get_client
    from elasticsearch.exceptions import RequestError
except ImportError:
    get_client = None

# from lino.api import rt
from lino.core.utils import get_models


class ESResolver:

    _resolved_indexes = None
    _resolved_json_indexes = None

    _indexes_file = Path(__file__).parent / 'search/indexes.json'

    @classmethod
    def get_models_by_index(cls, index, format_json=False):
        if cls._resolved_indexes is None:
            cls.resolve_es_indexes()
        if format_json:
            return cls._resolved_json_indexes[index]['models']
        return cls._resolved_indexes[index]['models']

    @classmethod
    def write_indexes(cls, filename=None):
        if cls._resolved_json_indexes is None:
            cls.resolve_es_indexes()
        if filename is None:
            filename = cls._indexes_file
        if isinstance(filename, str):
            filename = Path(filename)
        if filename.exists():
            mode = 'w'
            with open(filename, 'r') as f:
                json_indexes = json.load(f)
            if json_indexes == cls._resolved_json_indexes:
                modified = False
            else:
                modified = True
        else:
            mode = 'x'
            modified = True
        with open(filename, mode) as f:
            json.dump(cls._resolved_json_indexes, f)
        return modified

    @classmethod
    def read_indexes(cls, filename=None):
        if filename is None:
            filename = cls._indexes_file
        obj = None
        with open(filename, 'r') as f:
            obj = json.load(f)

        cls._resolved_json_indexes = obj
        return cls._resolved_json_indexes

    @classmethod
    def get_index_build(cls):
        if cls._resolved_indexes is None:
            cls.resolve_es_indexes()
        return cls._resolved_indexes

    @classmethod
    def get_indexes(cls):
        return cls.read_indexes().keys()

    @classmethod
    def resolve_es_indexes(cls, fmt_json=False):
        if cls._resolved_indexes is None:
            idxs = dict()
            idxs_json = dict()
            for m in get_models():
                if hasattr(m, 'ES_indexes') and m.ES_indexes is not None:
                    indexes = [i[0] for i in m.ES_indexes]
                    for index in indexes:
                        if index not in idxs:
                            idxs[index] = {'models': []}
                            idxs_json[index] = {'models': []}
                        idxs_json[index]['models'].append(m._meta.app_label + "." + m.__name__)
                        idxs[index]['models'].append(m)

            cls._resolved_indexes = idxs
            cls._resolved_json_indexes = idxs_json
        modified = cls.write_indexes()
        if fmt_json:
            return cls._resolved_json_indexes, modified
        return cls._resolved_indexes, modified

    @classmethod
    def create_index_mapping_files(cls):
        from lino.api import dd
        client = get_client()
        index_body = dd.plugins.search.DEFAULT_ES_INDEX_SETTINGS
        d = dd.plugins.search.mappings_dir
        for index, idict in cls.get_index_build().items():
            indexes = idict['models'][0].ES_indexes
            for i in indexes:
                if i[0] == index:
                    if len(i) > 1:
                        if 'settings' in i[1]:
                            index_body['settings'] = i[1].pop('settings')
                        if 'mappings' in i[1]:
                            index_body['mappings'] = i[1].pop('mappings')
                    break
            if 'mappings' in index_body:
                m = dict(mappings=index_body['mappings'])
            else:
                try:
                    # body = idict['models'][0].objects.first().as_search_document(index)
                    body = idict['models'][0].get_es_example_object(index=index)
                except:
                    raise Exception('Example object does not exist.')

                cls.force_index_creation(index, client=client, body=index_body)
                client.index(index=index, document=body)
                m = client.indices.get_mapping(index=index)[index]
                client.indices.delete(index=index)

                for field, value in m['mappings']['properties'].items():
                    if value.get('type', '') in ['text', 'match_only_text', 'search_as_you_type']:
                        value.update(analyzer='autocomplete', search_analyzer='autocomplete_search')
                        m['mappings']['properties'][field] = value

            file = d / (index + '.json')
            if file.exists():
                mode = 'w'
            else:
                mode = 'x'
            with open(file, mode) as f:
                json.dump(m, f)

    @classmethod
    def force_index_creation(cls, index, **kwargs):
        client = kwargs.pop('client')
        try:
            client.indices.create(index, **kwargs)
        except RequestError as e:
            assert str(e.error) == 'resource_already_exists_exception'
            client.indices.delete(index=index)
            client.indices.create(index, **kwargs)

    @classmethod
    def create_indexes(cls):
        from lino.api import dd
        client = get_client()
        d = dd.plugins.search.mappings_dir
        for index, idict in cls.get_index_build().items():
            index_body = dd.plugins.search.DEFAULT_ES_INDEX_SETTINGS.copy()
            indexes = idict['models'][0].ES_indexes
            file = d / (index + '.json')
            for i in indexes:
                if i[0] == index and len(i) > 1:
                    if 'settings' in i[1]:
                        index_body['settings'] = i[1].pop('settings')
                    if 'mappings' in i[1]:
                        index_body['mappings'] = i[1].pop('mappings')
                    elif file.exists():
                        with open(file, 'r') as f:
                            index_body['mappings'] = json.load(f)['mappings']
            if 'mappings' not in index_body:
                if not file.exists():
                    logger.warn('Dynamic mapping will be used for the index [%s]' % index)
                else:
                    with open(file, 'r') as f:
                        index_body['mappings'] = json.load(f)['mappings']
            cls.force_index_creation(index, client=client, body=index_body)

    @classmethod
    def populate_search_indexes_on_init(cls):
        client = get_client()
        indexes = cls.get_index_build()
        for index, models in indexes.items():
            for model in models['models']:
                for obj in model.objects.all():
                    obj.index_search_document(index=index)
                    # logger.info('.')
        # logger.info('\n')
