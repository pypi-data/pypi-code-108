from django.core.exceptions import ImproperlyConfigured

from security.config import settings

from .app import SecurityBackend


class BaseBackendReader:

    def get_count_input_requests(self, from_time, ip=None, path=None, view_slug=None, slug=None, method=None,
                                 exclude_log_id=None):
        raise NotImplementedError

    def get_logs_related_with_object(self, logger_name, related_object):
        raise NotImplementedError

    def get_stale_celery_task_invocation_logs(self):
        raise NotImplementedError


def get_reader_backend():
    if not SecurityBackend.registered_readers:
        raise ImproperlyConfigured('No registered backend reader was set')
    if settings.BACKEND_READER is not None:
        if settings.BACKEND_READER not in SecurityBackend.registered_readers:
            raise ImproperlyConfigured(f'Backend reader "{settings.BACKEND_READER}" is not registered')
        return SecurityBackend.registered_readers[settings.BACKEND_READER]
    else:
        return next(iter(SecurityBackend.registered_readers.values()))


def get_count_input_requests(from_time, ip=None, path=None, view_slug=None, slug=None, method=None,
                             exclude_log_id=None):
    return get_reader_backend().get_count_input_requests(
        from_time, ip, path, view_slug, slug, method, exclude_log_id
    )


def get_logs_related_with_object(logger_name, related_object):
    return get_reader_backend().get_logs_related_with_object(
        logger_name, related_object
    )
