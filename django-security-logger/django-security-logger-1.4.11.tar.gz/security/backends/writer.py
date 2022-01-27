import logging

from django.core.exceptions import ImproperlyConfigured

from security.backends.signals import (
    input_request_started, input_request_finished, input_request_error,
    output_request_started, output_request_finished, output_request_error,
    command_started, command_output_updated, command_finished, command_error,
    celery_task_invocation_started, celery_task_invocation_triggered, celery_task_invocation_ignored,
    celery_task_invocation_timeout, celery_task_invocation_expired,
    celery_task_run_started, celery_task_run_succeeded, celery_task_run_failed, celery_task_run_retried,
    celery_task_run_output_updated
)
from security.config import settings

from .app import SecurityBackend


logging_logger = logging.getLogger(__name__)


class BaseBackendWriter:

    CAPTURED_SIGNALS = {
        'input_request_started': input_request_started,
        'input_request_finished': input_request_finished,
        'input_request_error': input_request_error,

        'output_request_started': output_request_started,
        'output_request_finished': output_request_finished,
        'output_request_error': output_request_error,

        'command_started': command_started,
        'command_output_updated': command_output_updated,
        'command_finished': command_finished,
        'command_error': command_error,

        'celery_task_invocation_started': celery_task_invocation_started,
        'celery_task_invocation_triggered': celery_task_invocation_triggered,
        'celery_task_invocation_ignored': celery_task_invocation_ignored,
        'celery_task_invocation_timeout': celery_task_invocation_timeout,
        'celery_task_invocation_expired': celery_task_invocation_expired,

        'celery_task_run_started': celery_task_run_started,
        'celery_task_run_succeeded': celery_task_run_succeeded,
        'celery_task_run_failed': celery_task_run_failed,
        'celery_task_run_retried': celery_task_run_retried,
        'celery_task_run_output_updated': celery_task_run_output_updated,
    }

    def __init__(self, name):
        self._name = name
        self._init_signals()

    def _call_receiver_method(self, signal_name, logger):
        try:
            getattr(self, signal_name)(logger)
        except:  # noqa: E722
            logging_logger.error(f'Cannot write log {signal_name} for writer {self._name}', exc_info=True)

    def _get_receiver(self, signal_name):
        def _log_receiver(sender, logger, signal, **kwargs):
            if settings.BACKEND_WRITERS is None or self._name in settings.BACKEND_WRITERS:
                self._call_receiver_method(signal_name, logger)
        return _log_receiver

    def _init_signals(self):
        for signal_name, signal in self.CAPTURED_SIGNALS.items():
            signal.connect(self._get_receiver(signal_name), weak=False)

    def input_request_started(self, logger):
        raise NotImplementedError

    def input_request_finished(self, logger):
        raise NotImplementedError

    def input_request_error(self, logger):
        raise NotImplementedError

    def output_request_started(self, logger):
        raise NotImplementedError

    def output_request_finished(self, logger):
        raise NotImplementedError

    def output_request_error(self, logger):
        raise NotImplementedError

    def command_started(self, logger):
        raise NotImplementedError

    def command_output_updated(self, logger):
        raise NotImplementedError

    def command_finished(self, logger):
        raise NotImplementedError

    def command_error(self, logger):
        raise NotImplementedError

    def celery_task_invocation_started(self, logger):
        raise NotImplementedError

    def celery_task_invocation_triggered(self, logger):
        raise NotImplementedError

    def celery_task_invocation_ignored(self, logger):
        raise NotImplementedError

    def celery_task_invocation_timeout(self, logger):
        raise NotImplementedError

    def celery_task_invocation_expired(self, logger):
        raise NotImplementedError

    def celery_task_run_started(self, logger):
        raise NotImplementedError

    def celery_task_run_succeeded(self, logger):
        raise NotImplementedError

    def celery_task_run_failed(self, logger):
        raise NotImplementedError

    def celery_task_run_retried(self, logger):
        raise NotImplementedError

    def celery_task_run_output_updated(self, logger):
        raise NotImplementedError

    def set_stale_celery_task_log_state(self):
        pass

    def clean_logs(self, type, timestamp, backup_path, stdout):
        pass


def get_writer_backends():
    if not SecurityBackend.registered_readers:
        raise ImproperlyConfigured('No registered backend reader was set')
    if settings.BACKEND_WRITERS is not None:
        registered_writers = []
        for backend_name in settings.BACKEND_WRITERS:
            if backend_name not in SecurityBackend.registered_writers:
                raise ImproperlyConfigured(f'Backend writer "{backend_name}" is not registered')
            registered_writers.append(SecurityBackend.registered_writers[backend_name])
        return registered_writers
    else:
        return SecurityBackend.registered_writers.values()


def set_stale_celery_task_log_state():
    for writer in get_writer_backends():
        writer.set_stale_celery_task_log_state()


def clean_logs(type, timestamp, backup_path, stdout):
    for writer in get_writer_backends():
        writer.clean_logs(type, timestamp, backup_path, stdout)
