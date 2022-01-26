import os
import json
import gzip
import math

from io import TextIOWrapper

from datetime import datetime, time, timedelta

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now, utc
from django.utils.module_loading import import_string

from celery import current_app
from celery.exceptions import NotRegistered

from elasticsearch import ConflictError
from elasticsearch_dsl import Q

from security.config import settings
from security.enums import (
    RequestLogState, CeleryTaskInvocationLogState, CeleryTaskRunLogState, CommandState
)
from security.backends.common.helpers import get_parent_log_key_or_none
from security.backends.writer import BaseBackendWriter

from .models import (
    InputRequestLog, OutputRequestLog, CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog, get_key_from_object,
    get_response_state, get_log_model_from_logger_name
)


def lazy_serialize_qs_without_pk(qs):
    def generator():
        for obj in qs:
            yield obj.to_dict()

    class StreamList(list):
        def __iter__(self):
            return generator()

        def __len__(self):
            return 1

    return StreamList()


def get_querysets_by_batch(qs, batch):
    steps = math.ceil(qs.count() / batch)
    for step in range(steps):
        yield qs[step * batch:(step+1) * batch]


class ElasticsearchBackendWriter(BaseBackendWriter):

    def _get_related_object_keys(self, logger):
        return [
            get_key_from_object(related_object) for related_object in logger.related_objects
        ]

    def input_request_started(self, logger):
        input_request_log = InputRequestLog(
            slug=logger.slug,
            release=logger.release,
            related_objects=self._get_related_object_keys(logger),
            extra_data=logger.extra_data,
            state=RequestLogState.INCOMPLETE,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        input_request_log.meta.id = logger.id

        input_request_log.save()
        logger.backend_logs.elasticsearch = input_request_log

    def input_request_finished(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                state=get_response_state(logger.data['response_code']),
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def input_request_error(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def output_request_started(self, logger):
        output_request_log = OutputRequestLog(
            slug=logger.slug,
            release=logger.release,
            related_objects=self._get_related_object_keys(logger),
            extra_data=logger.extra_data,
            state=RequestLogState.INCOMPLETE,
            update_only_changed_fields=True,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        output_request_log.meta.id = logger.id
        output_request_log.save()
        logger.backend_logs.elasticsearch = output_request_log

    def output_request_finished(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                state=get_response_state(logger.data['response_code']),
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def output_request_error(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                state=RequestLogState.ERROR,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def command_started(self, logger):
        command_log = CommandLog(
            slug=logger.slug,
            release=logger.release,
            related_objects=self._get_related_object_keys(logger),
            extra_data=logger.extra_data,
            state=CommandState.ACTIVE,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        command_log.meta.id = logger.id
        command_log.save()
        logger.backend_logs.elasticsearch = command_log

    def command_output_updated(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def command_finished(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                state=CommandState.SUCCEEDED,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def command_error(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                state=CommandState.FAILED,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def celery_task_invocation_started(self, logger):
        celery_task_invocation_log = CeleryTaskInvocationLog(
            slug=logger.slug,
            release=logger.release,
            related_objects=self._get_related_object_keys(logger),
            extra_data=logger.extra_data,
            state=CeleryTaskInvocationLogState.WAITING,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        celery_task_invocation_log.meta.id = logger.id
        celery_task_invocation_log.save()
        logger.backend_logs.elasticsearch = celery_task_invocation_log

    def celery_task_invocation_triggered(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                extra_data=logger.extra_data,
                state=CeleryTaskInvocationLogState.TRIGGERED,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def celery_task_invocation_ignored(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                extra_data=logger.extra_data,
                state=CeleryTaskInvocationLogState.IGNORED,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def celery_task_invocation_timeout(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                extra_data=logger.extra_data,
                state=CeleryTaskInvocationLogState.TIMEOUT,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def celery_task_invocation_expired(self, logger):
        celery_task_invocation_log = CeleryTaskInvocationLog.get(id=logger.id)
        celery_task_invocation_log.update(
            slug=logger.slug,
            state=CeleryTaskInvocationLogState.EXPIRED,
            refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
            update_only_changed_fields=True,
            **logger.data
        )
        if celery_task_invocation_log.celery_task_id:
            CeleryTaskRunLog._index.refresh()
            celery_task_run_log_qs = CeleryTaskRunLog.search().filter(
                Q('term', celery_task_id=celery_task_invocation_log.celery_task_id)
                & Q('term', state=CeleryTaskRunLogState.ACTIVE.name)
            )
            for celery_task_run in celery_task_run_log_qs:
                celery_task_run.update(
                    state=CeleryTaskRunLogState.EXPIRED,
                    stop=logger.data['stop']
                )

    def celery_task_run_started(self, logger):
        celery_task_run_log = CeleryTaskRunLog(
            slug=logger.slug,
            release=logger.release,
            related_objects=self._get_related_object_keys(logger),
            extra_data=logger.extra_data,
            state=CeleryTaskRunLogState.ACTIVE,
            parent_log=get_parent_log_key_or_none(logger),
            **logger.data
        )
        celery_task_run_log.meta.id = logger.id
        celery_task_run_log.save()
        logger.backend_logs.elasticsearch = celery_task_run_log

    def celery_task_run_succeeded(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            celery_task_run_log = logger.backend_logs.elasticsearch
            celery_task_run_log.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                state=CeleryTaskRunLogState.SUCCEEDED,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

            CeleryTaskInvocationLog._index.refresh()
            celery_task_invocations_qs = CeleryTaskInvocationLog.search().filter(
                'term', celery_task_id=celery_task_run_log.celery_task_id
            ).query(
                Q('term', state=CeleryTaskInvocationLogState.WAITING.name)
                | Q('term', state=CeleryTaskInvocationLogState.TRIGGERED.name)
                | Q('term', state=CeleryTaskInvocationLogState.ACTIVE.name)
            )
            for celery_task_invocation in celery_task_invocations_qs:
                try:
                    celery_task_invocation.update(
                        state=CeleryTaskInvocationLogState.SUCCEEDED,
                        stop=logger.data['stop'],
                        refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                        update_only_changed_fields=True
                    )
                except ConflictError:
                    # conflict errors are ignored, celery task invocation was changed with another process
                    pass

    def celery_task_run_failed(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            celery_task_run_log = logger.backend_logs.elasticsearch
            celery_task_run_log.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                state=CeleryTaskRunLogState.FAILED,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

            CeleryTaskInvocationLog._index.refresh()
            celery_task_invocations_qs = CeleryTaskInvocationLog.search().filter(
                'term', celery_task_id=celery_task_run_log.celery_task_id
            ).query(
                Q('term', state=CeleryTaskInvocationLogState.WAITING.name)
                | Q('term', state=CeleryTaskInvocationLogState.TRIGGERED.name)
                | Q('term', state=CeleryTaskInvocationLogState.ACTIVE.name)
            )
            for celery_task_invocation in celery_task_invocations_qs:
                try:
                    celery_task_invocation.update(
                        state=CeleryTaskInvocationLogState.FAILED,
                        refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                        stop=logger.data['stop'],
                        update_only_changed_fields=True
                    )
                except ConflictError:
                    # conflict errors are ignored, celery task invocation was changed with another process
                    pass

    def celery_task_run_retried(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                related_objects=self._get_related_object_keys(logger),
                extra_data=logger.extra_data,
                state=CeleryTaskRunLogState.RETRIED,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data
            )

    def celery_task_run_output_updated(self, logger):
        if 'elasticsearch' in logger.backend_logs:
            logger.backend_logs.elasticsearch.update(
                slug=logger.slug,
                refresh=settings.ELASTICSEARCH_AUTO_REFRESH,
                update_only_changed_fields=True,
                retry_on_conflict=1,
                **logger.data,
            )

    def set_stale_celery_task_log_state(self):
        processsing_stale_tasks = CeleryTaskInvocationLog.search().filter(
            Q('range', stale_at={'lt': now()}) & Q(
                Q('term', state=CeleryTaskInvocationLogState.WAITING.name)
                | Q('term', state=CeleryTaskInvocationLogState.TRIGGERED.name)
                | Q('term', state=CeleryTaskInvocationLogState.ACTIVE.name)
            )
        ).sort('stale_at')
        for task in processsing_stale_tasks[:settings.SET_STALE_CELERY_INVOCATIONS_LIMIT_PER_RUN]:
            task_last_run = task.last_run
            if task_last_run and task_last_run.state == CeleryTaskRunLogState.SUCCEEDED:
                task.update(
                    state=CeleryTaskInvocationLogState.SUCCEEDED,
                    stop=task_last_run.stop,
                    update_only_changed_fields=True
                )
            elif task_last_run and task_last_run.state == CeleryTaskRunLogState.FAILED:
                task.update(
                    state=CeleryTaskInvocationLogState.FAILED,
                    stop=task_last_run.stop,
                    update_only_changed_fields=True
                )
            else:
                try:
                    current_app.tasks[task.name].expire_invocation(
                        task.id,
                        json.loads(task.task_args),
                        json.loads(task.task_kwargs),
                        dict(
                            start=task.start,
                            celery_task_id=task.celery_task_id,
                            stop=now(),
                            name=task.name,
                            queue_name=task.queue_name,
                        )
                    )
                except NotRegistered:
                    task.update(
                        state=CeleryTaskInvocationLogState.EXPIRED,
                        stop=now(),
                        update_only_changed_fields=True
                    )

    def clean_logs(self, type, timestamp, backup_path, stdout):
        storage = import_string(settings.BACKUP_STORAGE_CLASS)()

        qs = get_log_model_from_logger_name(type).search().filter(Q('range', stop={'lt': timestamp})).sort('stop')
        step_timestamp = None
        if qs.count() != 0:
            step_timestamp = list(qs[0:1])[0].stop

        while step_timestamp and step_timestamp < timestamp:
            min_timestamp = datetime.combine(step_timestamp, time.min).replace(tzinfo=utc)
            max_timestamp = datetime.combine(step_timestamp, time.max).replace(tzinfo=utc)

            qs_filtered_by_day = qs.filter(Q('range', stop={'gte': min_timestamp, 'lte': max_timestamp}))

            if qs_filtered_by_day.count() != 0:
                stdout.write(
                    2 * ' ' + 'Cleaning logs for date {} ({})'.format(
                        step_timestamp.date(), qs_filtered_by_day.count()
                    )
                )

                if backup_path:
                    for qs_batch in get_querysets_by_batch(qs_filtered_by_day, settings.PURGE_LOG_BACKUP_BATCH):
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
                qs_filtered_by_day.delete()

            step_timestamp = min_timestamp + timedelta(days=1)
