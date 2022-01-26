from elasticsearch import Elasticsearch

from kikyo import Kikyo
from kikyo.search import Search, Index


class EsBasedSearch(Search):
    def __init__(self, client: Kikyo):
        settings = client.settings.deep('elasticsearch')

        if not settings:
            return

        kwargs = {
            'hosts': settings['hosts']
        }
        if 'username' in settings:
            kwargs['http_auth'] = (settings['username'], settings['password'])
        if 'timeout' in settings:
            kwargs['timeout'] = settings['timeout']

        self.es = Elasticsearch(**kwargs)
        self.index_prefix = settings.get('index_prefix', default='')

        client.add_component('es_search', self)

    def get_index_of_topic(self, topic):
        if topic.startswith(self.index_prefix):
            return topic
        return f'{self.index_prefix}{topic}'

    def index(self, topic: str) -> Index:
        return EsIndex(topic, self)


class EsIndex(Index):
    def __init__(self, topic: str, client: EsBasedSearch):
        self.topic = topic
        self.es = client.es
        self.client = client

    def exists(self, id: str) -> bool:
        return self.es.exists(
            self.client.get_index_of_topic(self.topic),
            id,
        )

    def get(self, id: str) -> dict:
        resp = self.es.get(
            self.client.get_index_of_topic(self.topic),
            id,
        )
        return resp['_source']

    def put(self, id: str, data: dict):
        self.es.index(
            self.client.get_index_of_topic(self.topic),
            body=data,
            id=id,
        )

    def delete(self, id: str):
        self.es.delete(
            self.client.get_index_of_topic(self.topic),
            id,
        )
