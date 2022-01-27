import os
import json
import gzip
import math

from io import TextIOWrapper

from datetime import datetime, time

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import utc
from django.utils.timezone import now
from django.utils.module_loading import import_string

from celery import current_app
from celery.exceptions import NotRegistered

from chamber.shortcuts import change_and_save

from security.backends.common.helpers import get_parent_log_key_or_none
from security.backends.writer import BaseBackendWriter
from security.config import settings
from security.enums import RequestLogState, CeleryTaskInvocationLogState, CeleryTaskRunLogState, CommandState

from .models import (
    InputRequestLog, OutputRequestLog, CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog,
    get_log_model_from_logger_name, get_response_state
)


def lazy_serialize_qs_without_pk(qs):
    def generator():
        for obj in qs.iterator():
            data = serializers.serialize('python', [obj])[0]
            yield data

    class StreamList(list):
        def __iter__(self):
            return generator()

        def __len__(self):
            return 1

    return StreamList()


def get_querysets_by_batch(qs, batch):
    steps = math.ceil(qs.count() / batch)
    for _ in range(steps):
        yield qs[:batch]


class SQLBackendWriter(BaseBackendWriter):

    def input_request_started(self, logger):
        input_request_log = InputRequestLog(
            id=logger.id,
            release=logger.release,
            slug=logger.slug,
            state=RequestLogState.INCOMPLETE,
            extra_data=logger.extra_data,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        input_request_log.save()
        input_request_log.related_objects.add(*logger.related_objects)
        logger.backend_logs.sql = input_request_log

    def input_request_finished(self, logger):
        if 'sql' in logger.backend_logs:
            input_request_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=get_response_state(logger.data['response_code']),
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            input_request_log.related_objects.add(*logger.related_objects)

    def input_request_error(self, logger):
        if 'sql' in logger.backend_logs:
            input_request_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            input_request_log.related_objects.add(*logger.related_objects)

    def output_request_started(self, logger):
        output_request_log = OutputRequestLog(
            id=logger.id,
            release=logger.release,
            state=RequestLogState.INCOMPLETE,
            extra_data=logger.extra_data,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        output_request_log.save()
        output_request_log.related_objects.add(*logger.related_objects)
        logger.backend_logs.sql = output_request_log

    def output_request_finished(self, logger):
        if 'sql' in logger.backend_logs:
            output_request_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=get_response_state(logger.data['response_code']),
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            output_request_log.related_objects.add(*logger.related_objects)

    def output_request_error(self, logger):
        if 'sql' in logger.backend_logs:
            output_request_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=RequestLogState.ERROR,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            output_request_log.related_objects.add(*logger.related_objects)

    def command_started(self, logger):
        command_log = CommandLog(
            id=logger.id,
            release=logger.release,
            slug=logger.slug,
            state=CommandState.ACTIVE,
            extra_data=logger.extra_data,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        command_log.save()
        command_log.related_objects.add(*logger.related_objects)
        logger.backend_logs.sql = command_log

    def command_output_updated(self, logger):
        if 'sql' in logger.backend_logs:
            change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                update_only_changed_fields=True,
                **logger.data
            )

    def command_finished(self, logger):
        if 'sql' in logger.backend_logs:
            command_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=CommandState.SUCCEEDED,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            command_log.related_objects.add(*logger.related_objects)

    def command_error(self, logger):
        if 'sql' in logger.backend_logs:
            command_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=CommandState.FAILED,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            command_log.related_objects.add(*logger.related_objects)

    def celery_task_invocation_started(self, logger):
        celery_task_invocation_log = CeleryTaskInvocationLog(
            id=logger.id,
            release=logger.release,
            slug=logger.slug,
            state=CeleryTaskInvocationLogState.WAITING,
            extra_data=logger.extra_data,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        celery_task_invocation_log.save()
        celery_task_invocation_log.related_objects.add(*logger.related_objects)
        logger.backend_logs.sql = celery_task_invocation_log

    def celery_task_invocation_triggered(self, logger):
        if 'sql' in logger.backend_logs:
            change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=CeleryTaskInvocationLogState.TRIGGERED,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )

    def celery_task_invocation_ignored(self, logger):
        if 'sql' in logger.backend_logs:
            change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=CeleryTaskInvocationLogState.IGNORED,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )

    def celery_task_invocation_timeout(self, logger):
        if 'sql' in logger.backend_logs:
            change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=CeleryTaskInvocationLogState.TIMEOUT,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )

    def celery_task_invocation_expired(self, logger):
        celery_task_invocation_log = CeleryTaskInvocationLog.objects.update_or_create(
            id=logger.id,
            defaults=dict(
                slug=logger.slug,
                state=CeleryTaskInvocationLogState.EXPIRED,
                extra_data=logger.extra_data,
                **logger.data
            )
        )[0]
        celery_task_invocation_log.runs.filter(
            state=CeleryTaskRunLogState.ACTIVE
        ).change_and_save(
            state=CeleryTaskRunLogState.EXPIRED,
            stop=logger.data['stop']
        )

    def celery_task_run_started(self, logger):
        celery_task_run_log = CeleryTaskRunLog(
            id=logger.id,
            release=logger.release,
            slug=logger.slug,
            state=CeleryTaskRunLogState.ACTIVE,
            extra_data=logger.extra_data,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        celery_task_run_log.save()
        celery_task_run_log.related_objects.add(*logger.related_objects)
        logger.backend_logs.sql = celery_task_run_log

    def celery_task_run_succeeded(self, logger):
        if 'sql' in logger.backend_logs:
            celery_task_run_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=CeleryTaskRunLogState.SUCCEEDED,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            celery_task_run_log.get_task_invocation_logs().filter(state__in={
                CeleryTaskInvocationLogState.WAITING,
                CeleryTaskInvocationLogState.TRIGGERED,
                CeleryTaskInvocationLogState.ACTIVE
            }).change_and_save(
                state=CeleryTaskInvocationLogState.SUCCEEDED,
                stop=logger.data['stop']
            )
            celery_task_run_log.related_objects.add(*logger.related_objects)

    def celery_task_run_failed(self, logger):
        if 'sql' in logger.backend_logs:
            celery_task_run_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=CeleryTaskRunLogState.FAILED,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            celery_task_run_log.get_task_invocation_logs().filter(state__in={
                CeleryTaskInvocationLogState.WAITING,
                CeleryTaskInvocationLogState.TRIGGERED,
                CeleryTaskInvocationLogState.ACTIVE
            }).change_and_save(
                state=CeleryTaskInvocationLogState.FAILED,
                stop=logger.data['stop']
            )
            celery_task_run_log.related_objects.add(*logger.related_objects)

    def celery_task_run_retried(self, logger):
        if 'sql' in logger.backend_logs:
            celery_task_run_log = change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                state=CeleryTaskRunLogState.RETRIED,
                extra_data=logger.extra_data,
                update_only_changed_fields=True,
                **logger.data
            )
            celery_task_run_log.related_objects.add(*logger.related_objects)

    def celery_task_run_output_updated(self, logger):
        if 'sql' in logger.backend_logs:
            change_and_save(
                logger.backend_logs.sql,
                slug=logger.slug,
                update_only_changed_fields=True,
                **logger.data
            )

    def set_stale_celery_task_log_state(self):
        processsing_stale_tasks = CeleryTaskInvocationLog.objects.filter_processing(
            stale_at__lt=now()
        ).order_by('stale_at')
        for task in processsing_stale_tasks[:settings.SET_STALE_CELERY_INVOCATIONS_LIMIT_PER_RUN]:
            task_last_run = task.last_run
            if task_last_run and task_last_run.state == CeleryTaskRunLogState.SUCCEEDED:
                change_and_save(
                    task,
                    state=CeleryTaskInvocationLogState.SUCCEEDED,
                    stop=task_last_run.stop,
                    update_only_changed_fields=True
                )
            elif task_last_run and task_last_run.state == CeleryTaskRunLogState.FAILED:
                change_and_save(
                    task,
                    state=CeleryTaskInvocationLogState.FAILED,
                    stop=task_last_run.stop,
                    update_only_changed_fields=True
                )
            else:
                try:
                    current_app.tasks[task.name].expire_invocation(
                        task.id,
                        task.task_args,
                        task.task_kwargs,
                        dict(
                            start=task.start,
                            celery_task_id=task.celery_task_id,
                            stop=now(),
                            name=task.name,
                            queue_name=task.queue_name,
                        )
                    )
                except NotRegistered:
                    change_and_save(
                        task,
                        state=CeleryTaskInvocationLogState.EXPIRED,
                        stop=now(),
                        update_only_changed_fields=True
                    )

    def clean_logs(self, type, timestamp, backup_path, stdout):
        storage = import_string(settings.BACKUP_STORAGE_CLASS)()

        qs = get_log_model_from_logger_name(type).objects.filter(stop__lte=timestamp).order_by('stop')
        for step_timestamp in qs.datetimes('start', 'day', tzinfo=utc):
            min_timestamp = datetime.combine(step_timestamp, time.min).replace(tzinfo=utc)
            max_timestamp = datetime.combine(step_timestamp, time.max).replace(tzinfo=utc)
            qs_filtered_by_day = qs.filter(stop__range=(min_timestamp, max_timestamp))

            for qs_batch in get_querysets_by_batch(qs_filtered_by_day, settings.PURGE_LOG_BACKUP_BATCH):
                stdout.write(
                    2 * ' ' + 'Cleaning logs for date {} ({})'.format(
                        step_timestamp.date(), qs_batch.count()
                    )
                )
                if backup_path:
                    log_file_name = os.path.join(backup_path, str(step_timestamp.date()))

                    if storage.exists('{}.json.gz'.format(log_file_name)):
                        i = 1
                        while storage.exists('{}({}).json.gz'.format(log_file_name, i)):
                            i += 1
                        log_file_name = '{}({})'.format(log_file_name, i)

                    stdout.write(4 * ' ' + 'generating backup file: {}.json.gz'.format(log_file_name))

                    with storage.open('{}.json.gz'.format(log_file_name), 'wb') as f:
                        with TextIOWrapper(gzip.GzipFile(filename='{}.json'.format(log_file_name),
                                                         fileobj=f, mode='wb')) as gzf:
                            json.dump(
                                lazy_serialize_qs_without_pk(qs_batch), gzf, cls=DjangoJSONEncoder, indent=5
                            )

                stdout.write(4 * ' ' + 'deleting logs')
                for qs_batch_to_delete in get_querysets_by_batch(qs_batch, settings.PURGE_LOG_DELETE_BATCH):
                    qs_filtered_by_day.filter(pk__in=qs_batch_to_delete).delete()
