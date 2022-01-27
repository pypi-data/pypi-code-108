from security.backends.reader import BaseBackendReader

from .models import InputRequestLog, get_log_model_from_logger_name


class SQLBackendReader(BaseBackendReader):

    def get_count_input_requests(self, from_time, ip=None, path=None, view_slug=None, slug=None, method=None,
                                 exclude_log_id=None):
        qs = InputRequestLog.objects.filter(
            start__gte=from_time,
        )
        if ip is not None:
            qs = qs.filter(ip=ip)
        if path is not None:
            qs = qs.filter(path=path)
        if method is not None:
            qs = qs.filter(method=method)
        if view_slug is not None:
            qs = qs.filter(view_slug=view_slug)
        if slug is not None:
            qs = qs.filter(slug=slug)
        if exclude_log_id is not None:
            qs = qs.exclude(pk=exclude_log_id)
        return qs.count()

    def get_logs_related_with_object(self, logger_name, related_object):
        return list(get_log_model_from_logger_name(logger_name).objects.filter_related_with_object(related_object))
