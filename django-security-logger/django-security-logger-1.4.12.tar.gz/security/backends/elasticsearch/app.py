from security.backends.app import SecurityBackend


class SecurityElasticsearchBackend(SecurityBackend):

    name = 'security.backends.elasticsearch'
    label = 'security_backends_elasticsearch'
    backend_name = 'elasticsearch'
    writer = 'security.backends.elasticsearch.writer.ElasticsearchBackendWriter'
    reader = 'security.backends.elasticsearch.reader.ElasticsearchBackendReader'
