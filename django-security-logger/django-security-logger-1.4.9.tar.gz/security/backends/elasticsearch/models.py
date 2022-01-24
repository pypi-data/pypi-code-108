import json

from elasticsearch import NotFoundError

from django.db import router
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from django.core.serializers.json import DjangoJSONEncoder

from elasticsearch_dsl import Q
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, Object, Boolean, Float, CustomField

from security.backends.common.mixins import (
    CeleryTaskInvocationLogStrMixin, CeleryTaskRunLogStrMixin, CommandLogStrMixin, InputRequestLogStrMixin,
    LogShortIdMixin, OutputRequestLogStrMixin
)
from security.config import settings
from security.enums import (
    RequestLogState, CeleryTaskInvocationLogState, CeleryTaskRunLogState, CommandState, LoggerName
)

from .connection import set_connection


class JSONTextField(CustomField):

    name = 'jsontext'
    builtin_type = Text()

    def serialize(self, data):
        if data is None:
            return None
        elif isinstance(data, str):
            return data
        else:
            return json.dumps(data, cls=DjangoJSONEncoder)


class EnumField(CustomField):

    name = 'enum'
    builtin_type = Keyword()

    def __init__(self, enum):
        self._enum = enum

    def _serialize(self, data):
        return data.name

    def _deserialize(self, data):
        if isinstance(data, self._enum):
            return data
        else:
            return self._enum[data]


class Log(LogShortIdMixin, Document):

    extra_data = Object()
    slug = Keyword()
    related_objects = Keyword()
    parent_log = Keyword()
    start = Date()
    stop = Date()
    time = Float()
    release = Keyword()

    def __str__(self):
        return self.id

    @classmethod
    def _get_using(cls, using=None):
        set_connection()
        return super()._get_using(using)

    def _set_time(self, kwargs):
        start = kwargs.get('start', self.start)
        stop = kwargs.get('stop', self.stop)
        time = kwargs.get('time', self.time)
        if not time and start and stop:
            kwargs['time'] = (stop - start).total_seconds()

    def save(self, **kwargs):
        self._set_time(kwargs)
        return super().save(**kwargs)

    @property
    def id(self):
        return self.meta.id

    @property
    def pk(self):
        return self.id

    def update(
        self,
        using=None,
        index=None,
        detect_noop=True,
        doc_as_upsert=False,
        refresh=False,
        retry_on_conflict=None,
        script=None,
        script_id=None,
        scripted_upsert=False,
        upsert=None,
        return_doc_meta=False,
        update_only_changed_fields=False,
        **fields
    ):
        self._set_time(fields)
        if update_only_changed_fields:
            fields = {k: v for k, v in fields.items() if getattr(self, k) != v}
        if fields:
            super().update(
                using, index, detect_noop, doc_as_upsert, refresh, retry_on_conflict, script, script_id,
                scripted_upsert, upsert, return_doc_meta, **fields
            )


class RequestLog(Log):

    host = Keyword()
    method = Keyword()
    path = Keyword()
    queries = JSONTextField()
    is_secure = Boolean()

    # Request information
    request_headers = JSONTextField()
    request_body = Text()

    # Response information
    response_code = Keyword()
    response_headers = JSONTextField()
    response_body = Text()

    state = EnumField(enum=RequestLogState)
    error_message = Text()


class InputRequestLog(InputRequestLogStrMixin, RequestLog):

    user_id = Keyword()
    ip = Keyword()
    view_slug = Keyword()

    class Index:
        name = '{}-input-request-log'.format(settings.ELASTICSEARCH_DATABASE.get('prefix', 'security'))

    @cached_property
    def user(self):
        return get_user_model().objects.filter(pk=self.user_id).first()


class OutputRequestLog(OutputRequestLogStrMixin, RequestLog):

    class Index:
        name = '{}-output-request-log'.format(settings.ELASTICSEARCH_DATABASE.get('prefix', 'security'))


class CommandLog(CommandLogStrMixin, Log):

    name = Keyword()
    input = Text()
    is_executed_from_command_line = Boolean()
    output = Text()
    is_successful = Boolean()
    state = EnumField(enum=CommandState)
    error_message = Text()

    class Index:
        name = '{}-command-log'.format(settings.ELASTICSEARCH_DATABASE.get('prefix', 'security'))


class CeleryTaskInvocationLog(CeleryTaskInvocationLogStrMixin, Log):

    celery_task_id = Keyword()
    name = Keyword()
    queue_name = Keyword()
    applied_at = Date()
    triggered_at = Date()
    is_unique = Boolean()
    is_async = Boolean()
    is_duplicate = Boolean()
    is_on_commit = Boolean()
    input = Text()
    task_args = JSONTextField()
    task_kwargs = JSONTextField()
    estimated_time_of_first_arrival = Date()
    expires_at = Date()
    stale_at = Date()
    state = EnumField(enum=CeleryTaskInvocationLogState)

    @property
    def last_run(self):
        runs = CeleryTaskRunLog.search().filter(
            Q('term', celery_task_id=self.celery_task_id)
        ).sort('-start').execute()
        return runs[0] if runs else None

    class Index:
        name = '{}-celery-task-invocation-log'.format(settings.ELASTICSEARCH_DATABASE.get('prefix', 'security'))


class CeleryTaskRunLog(CeleryTaskRunLogStrMixin, Log):

    celery_task_id = Keyword()
    state = EnumField(enum=CeleryTaskRunLogState)
    name = Keyword()
    input = Text()
    task_args = JSONTextField()
    task_kwargs = JSONTextField()
    result = JSONTextField()
    error_message = Text()
    output = Text()
    retries = Integer()
    estimated_time_of_next_retry = Date()
    queue_name = Keyword()
    waiting_time = Float()

    class Index:
        name = '{}-celery-task-run-log'.format(settings.ELASTICSEARCH_DATABASE.get('prefix', 'security'))


def _get_content_type(model, using=None):
    return ContentType.objects.db_manager(using).get_for_model(model)


def get_key_from_content_type_and_id(content_type, object_id, model_db=None):
    model_db = model_db or router.db_for_write(content_type.model_class())
    return '|'.join((model_db, str(content_type.pk), str(object_id)))


def get_key_from_object(obj, model_db=None):
    return get_key_from_content_type_and_id(_get_content_type(obj), obj.pk, model_db)


def get_object_from_key(key):
    model_db, content_type_id, object_id = key.split('|')
    return ContentType.objects.get(
        pk=content_type_id
    ).model_class().objects.using(model_db).filter(pk=object_id).first()


def get_response_state(status_code):
    if status_code >= 500:
        return RequestLogState.ERROR
    elif status_code >= 400:
        return RequestLogState.WARNING
    else:
        return RequestLogState.INFO


logger_name_to_log_model = {
    LoggerName.INPUT_REQUEST: InputRequestLog,
    LoggerName.OUTPUT_REQUEST: OutputRequestLog,
    LoggerName.COMMAND: CommandLog,
    LoggerName.CELERY_TASK_INVOCATION: CeleryTaskInvocationLog,
    LoggerName.CELERY_TASK_RUN: CeleryTaskRunLog,
}


def get_log_model_from_logger_name(logger_name):
    return logger_name_to_log_model[logger_name]


def get_log_from_key(key):
    try:
        logger_name, id = key.split('|')
        return get_log_model_from_logger_name(logger_name).get(id=id)
    except NotFoundError:
        return None


def get_log_key(log):
    logger_name = {v: k for k, v in logger_name_to_log_model.items()}[log.__class__]
    return '{}|{}'.format(logger_name, log.meta.id)
