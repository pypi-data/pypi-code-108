from elasticsearch_dsl import connections

from django.core.exceptions import ImproperlyConfigured

from security.config import settings


class ConnectionHandler:

    connection = None

    def connect(self, init_documents):
        if not self.connection:
            if not settings.ELASTICSEARCH_DATABASE:
                raise ImproperlyConfigured('You must set "SECURITY_ELASTICSEARCH_DATABASE" setting')

            connection.connection = connections.create_connection(
                **settings.ELASTICSEARCH_DATABASE
            )
            if init_documents:
                self.init_documents()

    def init_documents(self):
        from security.backends.elasticsearch.models import (
            InputRequestLog, OutputRequestLog, CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog
        )

        for document in InputRequestLog, OutputRequestLog, CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog:
            document.init()


connection = ConnectionHandler()


def set_connection(init_documents=True):
    connection.connect(init_documents)
