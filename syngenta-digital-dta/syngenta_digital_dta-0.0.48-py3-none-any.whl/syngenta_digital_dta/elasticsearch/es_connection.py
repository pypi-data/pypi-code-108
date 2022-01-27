from syngenta_digital_dta.elasticsearch.es_connector import ESConnector


def es_connection(func):
    __connections = {}
    def decorator(obj):
        if not __connections.get(obj.endpoint):
            es_connector = ESConnector(obj)
            __connections[obj.endpoint] = es_connector.connect()
        obj.connection = __connections[obj.endpoint]
        return func(obj)
    return decorator
