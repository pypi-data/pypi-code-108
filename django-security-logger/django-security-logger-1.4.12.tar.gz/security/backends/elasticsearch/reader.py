from elasticsearch_dsl import Q

from security.backends.reader import BaseBackendReader

from .models import InputRequestLog, get_log_model_from_logger_name, get_key_from_object


class ElasticsearchBackendReader(BaseBackendReader):

    def get_count_input_requests(self, from_time, ip=None, path=None, view_slug=None, slug=None, method=None,
                                 exclude_log_id=None):
        q = Q('range', start={'gte': from_time})

        if ip is not None:
            q &= Q('term', ip=ip)
        if path is not None:
            q &= Q('term', path=path)
        if method is not None:
            q &= Q('term', method=method)
        if view_slug is not None:
            q &= Q('term', view_slug=view_slug)
        if slug is not None:
            q &= Q('term', slug=slug)
        if exclude_log_id is not None:
            q &= ~Q('ids', **{'values': [exclude_log_id]})
        return InputRequestLog.search().filter(q).count()

    def get_logs_related_with_object(self, logger_name, related_object):
        related_object_key = get_key_from_object(related_object)
        return list(get_log_model_from_logger_name(logger_name).search().filter(
            Q('term', related_objects=related_object_key)
        ))
