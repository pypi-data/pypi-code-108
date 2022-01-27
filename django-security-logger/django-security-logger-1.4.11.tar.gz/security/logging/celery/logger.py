from django.utils.timezone import now

from security.enums import LoggerName
from security.logging.common import SecurityLogger
from security.backends.signals import (
    celery_task_invocation_started, celery_task_invocation_triggered, celery_task_invocation_ignored,
    celery_task_invocation_timeout, celery_task_invocation_expired, celery_task_run_started, celery_task_run_succeeded,
    celery_task_run_failed, celery_task_run_retried, celery_task_run_output_updated
)


class CeleryInvocationLogger(SecurityLogger):

    name = LoggerName.CELERY_TASK_INVOCATION
    store = False

    def log_started(self, name, queue_name, task_args, task_kwargs, applied_at,
                    is_async, is_unique, is_on_commit):
        task_input = []
        if task_args:
            task_input += [str(v) for v in task_args]
        if task_kwargs:
            task_input += ['{}={}'.format(k, v) for k, v in task_kwargs.items()]
        self.data.update(dict(
            name=name,
            queue_name=queue_name,
            input=', '.join(task_input),
            task_args=list(task_args),
            task_kwargs=task_kwargs,
            applied_at=applied_at,
            is_async=is_async,
            is_unique=is_unique,
            is_on_commit=is_on_commit,
            start=now()
        ))
        celery_task_invocation_started.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_triggered(self, triggered_at, stale_at, estimated_time_of_first_arrival,
                      expires_at, celery_task_id):
        self.data.update(dict(
            triggered_at=triggered_at,
            stale_at=stale_at,
            estimated_time_of_first_arrival=estimated_time_of_first_arrival,
            expires_at=expires_at,
            celery_task_id=celery_task_id,
            is_duplicate=False
        ))
        celery_task_invocation_triggered.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_unique(self, triggered_at, stale_at, estimated_time_of_first_arrival,
                   expires_at, celery_task_id):
        self.data.update(dict(
            triggered_at=triggered_at,
            stale_at=stale_at,
            estimated_time_of_first_arrival=estimated_time_of_first_arrival,
            expires_at=expires_at,
            celery_task_id=celery_task_id,
            is_duplicate=True
        ))
        celery_task_invocation_triggered.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_ignored(self):
        self.data.update(dict(
            stop=now()
        ))
        celery_task_invocation_ignored.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_timeout(self):
        self.data.update(dict(
            stop=now()
        ))
        celery_task_invocation_timeout.send(
            sender=CeleryInvocationLogger,
            logger=self,
        )

    def log_expired(self, name):
        self.data.update(dict(
            stop=now()
        ))
        celery_task_invocation_expired.send(
            sender=CeleryInvocationLogger,
            name=name,
            logger=self,
        )


class CeleryTaskRunLogger(SecurityLogger):

    name = LoggerName.CELERY_TASK_RUN

    def log_started(self, name, queue_name, task_args, task_kwargs, celery_task_id, retries, trigger_time):
        task_input = []
        if task_args:
            task_input += [str(v) for v in task_args]
        if task_kwargs:
            task_input += ['{}={}'.format(k, v) for k, v in task_kwargs.items()]
        start = now()
        self.data.update(dict(
            name=name,
            celery_task_id=celery_task_id,
            queue_name=queue_name,
            input=', '.join(task_input),
            task_args=list(task_args),
            task_kwargs=task_kwargs,
            start=start,
            retries=retries,
            waiting_time=(start - trigger_time).total_seconds(),
        ))
        celery_task_run_started.send(
            sender=CeleryTaskRunLogger,
            logger=self,
        )

    def log_succeeded(self, result):
        self.data.update(dict(
            result=result,
            stop=now(),
        ))
        celery_task_run_succeeded.send(
            sender=CeleryTaskRunLogger,
            logger=self,
        )

    def log_failed(self, ex_tb):
        self.data.update(dict(
            error_message=ex_tb,
            stop=now(),
        ))
        celery_task_run_failed.send(
            sender=CeleryTaskRunLogger,
            logger=self,
        )

    def log_retried(self, ex_tb, estimated_time_of_next_retry):
        self.data.update(dict(
            error_message=ex_tb,
            stop=now(),
            estimated_time_of_next_retry=estimated_time_of_next_retry
        ))
        celery_task_run_retried.send(
            sender=CeleryTaskRunLogger,
            logger=self,
        )

    def log_output_updated(self, output):
        self.data['output'] = output
        celery_task_run_output_updated.send(sender=CeleryTaskRunLogger, logger=self)
