from syngenta_digital_dta.common import schema_mapper
from syngenta_digital_dta.common.base_adapter import BaseAdapter
from syngenta_digital_dta.elasticsearch.es_connection import es_connection
from syngenta_digital_dta.elasticsearch import es_mapper


class ElasticsearchAdapter(BaseAdapter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.index = kwargs['index']
        self.endpoint = kwargs['endpoint']
        self.model_schema_file = kwargs['model_schema_file']
        self.model_schema = kwargs['model_schema']
        self.model_identifier = kwargs['model_identifier']
        self.authentication = kwargs.get('authentication')
        self.port = kwargs.get('port')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.size = kwargs.get('size', 10)
        self.connection = None
        self.__connect()

    @es_connection
    def __connect(self):
        # just need to call to invoke the decorator
        pass

    def create_template(self, **kwargs):
        kwargs['use_patterns'] = True
        body = self.__create_template_body(**kwargs)
        self.connection.indices.put_template(
            name=f'{kwargs["name"]}-template',
            body=body
        )

    def create_index(self, **kwargs):
        if not self.connection.indices.exists(self.index):
            create_args = {}
            create_args['index'] = self.index
            if kwargs.get('template', True):
                create_args['body'] = self.__create_template_body(**kwargs)
            self.connection.indices.create(**create_args)

    def create(self, **kwargs):
        data = schema_mapper.map_to_schema(kwargs['data'], self.model_schema_file, self.model_schema)
        response = self.connection.index(
            index=self.index,
            id=data[self.model_identifier],
            body=data,
            op_type='create',
            refresh=kwargs.get('refresh', True)
        )
        super().publish('create', data)
        return response

    def update(self, **kwargs):
        response = self.connection.update(
            index=self.index,
            id=kwargs['data'][self.model_identifier],
            body={'doc': kwargs['data']},
            refresh=kwargs.get('refresh', True)
        )
        super().publish('update', kwargs['data'])
        return response

    def upsert(self, **kwargs):
        if self.connection.exists(index=self.index, id=kwargs['data'][self.model_identifier]):
            return self.update(**kwargs)
        return self.create(**kwargs)

    def delete(self, identifier_value, **kwargs):
        response = self.connection.delete(
            index=self.index,
            id=identifier_value,
            refresh=kwargs.get('refresh', True)
        )
        super().publish('delete', {self.model_identifier: identifier_value})
        return response

    def get(self, identifier_value, **kwargs):
        try:
            response = self.connection.get(index=self.index, id=identifier_value)
            if kwargs.get('normalize'):
                response = response.get('_source')
        except:
            response = {}
        return response

    def query(self, **kwargs):
        response = self.connection.search(
            index=self.index,
            size=self.size,
            body={'query': kwargs['query']}
        )
        if kwargs.get('normalize'):
            response = self.__normalize_hits(response)
        return response

    def __normalize_hits(self, hits):
        normalized_hits = []
        for hit in hits.get('hits', {}).get('hits', []):
            normalized_hits.append(hit['_source'])
        return normalized_hits

    def __create_template_body(self, **kwargs):
        body = {
            'settings': self.__get_settings(**kwargs),
            'mappings': self.__convert_openapi_mapping(self.model_schema_file, self.model_schema, kwargs.get('special'))
        }
        if kwargs.get('use_patterns') and isinstance(kwargs['index_patterns'], list):
            body['index_patterns'] = kwargs['index_patterns']
        elif kwargs.get('use_patterns'):
            body['index_patterns'] = [kwargs['index_patterns']]
        return body

    def __get_settings(self, **kwargs):
        if kwargs.get('settings'):
            return kwargs['settings']
        settings = {
            'number_of_replicas': 1,
            'number_of_shards': 1,
            "analysis": {
                "analyzer": {
                    "url_email_analyzer": {
                        "type": "custom",
                        "tokenizer": "uax_url_email"
                    }
                }
            }
        }
        return settings

    def __convert_openapi_mapping(self, schema_file, schema_key, special=None):
        mapping = es_mapper.convert_schema_to_mapping(schema_file, schema_key, special)
        return mapping
