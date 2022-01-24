from uuid import uuid4

from django.test.utils import override_settings

from .models import CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog, InputRequestLog, OutputRequestLog


class store_elasticsearch_log(override_settings):

    def __init__(self):
        super().__init__(SECURITY_BACKEND_WRITERS=('elasticsearch',), SECURITY_ELASTICSEARCH_AUTO_REFRESH=True)

    def enable(self):
        super().enable()
        uuid = uuid4()
        for document_class in (CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog,
                               InputRequestLog, OutputRequestLog):
            document_class._index._name = f'{uuid}.{document_class._index._name}'
            document_class.init()

    def disable(self):
        for document_class in (CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog,
                               InputRequestLog, OutputRequestLog):
            document_class._index.delete()
            document_class._index._name = document_class._index._name.split('.', 1)[1]
        super().disable()
