import logging

from datetime import timedelta

from django.core.management.base import OutputWrapper
from django.db import transaction

from django_celery_extensions.task import DjangoTask, ResultWrapper

from celery.utils.time import maybe_iso8601

from chamber.utils.transaction import pre_commit, in_atomic_block

from security.config import settings
from security.utils import LogStringIO
from security.logging.celery.logger import CeleryTaskRunLogger, CeleryInvocationLogger


logger = logging.getLogger(__name__)


class LoggedResultWrapper(ResultWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invocation_log = CeleryInvocationLogger(
            self._invocation_id, related_objects=self._options.pop('related_objects', [])
        )

    def on_apply(self):
        self.invocation_log.log_started(
            name=self._task.name,
            queue_name=self._options['queue'],
            task_args=self._args or [],
            task_kwargs=self._kwargs or {},
            applied_at=self._options['apply_time'],
            is_async=self._options['is_async'],
            is_unique=self._task.unique,
            is_on_commit=self._options['is_on_commit']
        )

    def on_trigger(self):
        stale_time_limit = self._options.get('stale_time_limit')
        self.invocation_log.log_triggered(
            triggered_at=self._options.get('trigger_time'),
            stale_at=(
                self._options.get('trigger_time') + timedelta(seconds=stale_time_limit)
                if stale_time_limit is not None else None
            ),
            estimated_time_of_first_arrival=self._options.get('eta'),
            expires_at=self._options.get('expires'),
            celery_task_id=self._options.get('task_id')
        )

    def on_unique(self):
        stale_time_limit = self._options.get('stale_time_limit')
        self.invocation_log.log_unique(
            triggered_at=self._options.get('trigger_time'),
            stale_at=(
                self._options.get('trigger_time') + timedelta(seconds=stale_time_limit)
                if stale_time_limit is not None else None
            ),
            estimated_time_of_first_arrival=self._options.get('eta'),
            expires_at=self._options.get('expires'),
            celery_task_id=self._options.get('task_id')
        )

    def on_ignored(self):
        self.invocation_log.log_ignored()

    def on_timeout(self):
        self.invocation_log.log_timeout()


class LoggedTask(DjangoTask):

    abstract = True
    result_wrapper_class = LoggedResultWrapper

    def on_invocation_apply(self, invocation_id, args, kwargs, options, result):
        _super = super()

        def _on_invocation_apply():
            _super.on_invocation_apply(invocation_id, args, kwargs, options, result)

        if options.get('is_on_commit') and in_atomic_block():
            if settings.TASK_USE_PRE_COMMIT:
                pre_commit(_on_invocation_apply, using=options.get('using'))
            else:
                transaction.on_commit(_on_invocation_apply, using=options.get('using'))
        else:
            _on_invocation_apply()

    def on_task_start(self, task_id, args, kwargs):
        super().on_task_start(task_id, args, kwargs)
        run_logger = CeleryTaskRunLogger()
        self.request.run_logger = run_logger
        run_logger.log_started(
            name=self.name,
            queue_name=self.request.delivery_info.get('routing_key'),
            task_args=args,
            task_kwargs=kwargs,
            celery_task_id=task_id,
            retries=self.request.retries,
            trigger_time=maybe_iso8601(self._get_header_from_request('trigger_time'))
        )
        self.request.output_stream = LogStringIO(
            flush_callback=lambda output_stream: run_logger.log_output_updated(output_stream.getvalue())
        )

    def on_task_retry(self, task_id, args, kwargs, exc, eta):
        super().on_task_retry(task_id, args, kwargs, exc, eta)
        try:
            self.request.run_logger.log_retried(
                ex_tb=str(exc),
                estimated_time_of_next_retry=eta
            )
            self.request.output_stream.close()
        finally:
            self.request.run_logger.close()

    def on_task_success(self, task_id, args, kwargs, retval):
        super().on_task_success(task_id, args, kwargs, retval)
        try:
            self.request.run_logger.log_succeeded(
                result=retval
            )
            self.request.output_stream.close()
        finally:
            self.request.run_logger.close()

    def on_task_failure(self, task_id, args, kwargs, exc, einfo):
        super().on_task_failure(task_id, args, kwargs, exc, einfo)
        log_id = None
        if hasattr(self.request, 'run_logger'):
            log_id = self.request.run_logger.id
            self.request.run_logger.close()
            self.request.run_logger.log_failed(
                ex_tb=str(exc)
            )
            self.request.output_stream.close()

        logger.error(
            f'Task with name {self.name} raised exception',
            extra={
                'einfo': str(einfo),
                'exception': str(exc),
                'task_id': task_id,
                'log_id': log_id
            }
        )

    def expire_invocation(self, invocation_log_id, args, kwargs, logger_data):
        with CeleryInvocationLogger(invocation_log_id, data=logger_data) as invocation_logger:
            invocation_logger.log_expired(self.name)

        logger.error(
            f'Task with name {self.name} was expired',
            extra={
                'invocation_log_id': invocation_log_id
            }
        )

    @property
    def run_logger(self):
        return None if not self.request else self.request.run_logger

    @property
    def stdout(self):
        return OutputWrapper(self.request.output_stream)

    @property
    def stderr(self):
        return OutputWrapper(self.request.output_stream)

    @property
    def task_log(self):
        return self.request.celery_task_log

    def get_command_kwargs(self):
        return dict(
            stdout=self.request.output_stream,
            stderr=self.request.output_stream,
        )
