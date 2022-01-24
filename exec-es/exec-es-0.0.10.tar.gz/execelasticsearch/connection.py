from elasticsearch import Elasticsearch, RequestsHttpConnection


class ClientConfig:
    def __new__(
            cls,
            hosts: list = None,
            port=9200,
            use_ssl=False,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=10,
            doc_type=None,
            max_retries=3,
            retry_on_timeout=True,
            **kwargs):
        return {**{k: v for k, v in locals().items() if k not in ['cls', 'kwargs']}, **kwargs}


class Clients:
    def __init__(self, **kwargs):
        self.defult_args = ClientConfig()
        self.connect = {k: Elasticsearch(**{**self.defult_args, **v}) for k, v in kwargs.items()}

    def __getitem__(self, item) -> Elasticsearch:
        return self.connect[item]
