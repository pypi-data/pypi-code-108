from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.timezone import localtime

from generic_m2m_field.models import MultipleDBGenericManyToManyField

from chamber.models import SmartQuerySet

from enumfields import IntegerEnumField

from security.backends.common.mixins import (
    CeleryTaskInvocationLogStrMixin, CeleryTaskRunLogStrMixin, CommandLogStrMixin, InputRequestLogStrMixin,
    LogShortIdMixin, OutputRequestLogStrMixin
)
from security.enums import (
    LoggerName, RequestLogState, CeleryTaskInvocationLogState, CeleryTaskRunLogState, CommandState
)


class BaseLogQuerySet(SmartQuerySet):

    def filter_related_with_object(self, related_object):
        return self.filter(
            related_objects__object_id=related_object.pk,
            related_objects__object_ct_id=ContentType.objects.get_for_model(related_object).pk
        )


class Log(LogShortIdMixin, models.Model):

    id = models.UUIDField(
        null=False,
        blank=False,
        max_length=250,
        primary_key=True
    )
    extra_data = models.JSONField(
        null=True,
        blank=True,
        encoder=DjangoJSONEncoder
    )
    slug = models.CharField(
        null=True,
        blank=True,
        db_index=True,
        max_length=255
    )
    start = models.DateTimeField(
        blank=False,
        null=False,
        editable=False
    )
    stop = models.DateTimeField(
        blank=True,
        null=True,
        editable=False
    )
    time = models.FloatField(
        null=True,
        blank=True
    )
    release = models.CharField(
        null=True,
        blank=True,
        db_index=True,
        max_length=255
    )
    parent_log = models.CharField(
        null=True,
        blank=True,
        db_index=True,
        max_length=250
    )

    def save(self, update_fields=None, *args, **kwargs):
        if not self.time and self.start and self.stop:
            self.time = (self.stop - self.start).total_seconds()
            if update_fields:
                update_fields = list(update_fields) + ['time']
        super().save(update_fields=update_fields, *args, **kwargs)

    class Meta:
        abstract = True


class RequestLog(Log):

    host = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        db_index=True
    )
    method = models.SlugField(
        max_length=7,
        null=False,
        blank=False,
        db_index=True
    )
    path = models.CharField(
        max_length=2000,
        null=False,
        blank=True,
        db_index=True
    )
    queries = models.JSONField(
        null=True,
        blank=True,
        encoder=DjangoJSONEncoder
    )
    is_secure = models.BooleanField(
        default=False,
        null=False,
        blank=False
    )

    # Request information
    request_headers = models.JSONField(
        null=True,
        blank=True,
        encoder=DjangoJSONEncoder
    )
    request_body = models.TextField(
        null=True,
        blank=True
    )

    # Response information
    response_code = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )
    response_headers = models.JSONField(
        null=True,
        blank=True,
        encoder=DjangoJSONEncoder
    )
    response_body = models.TextField(
        null=True,
        blank=True
    )

    state = IntegerEnumField(
        enum=RequestLogState,
        null=False,
        blank=False,
        default=RequestLogState.INCOMPLETE
    )
    error_message = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return ' '.join(
            (force_text(v) for v in (
                self.slug, self.response_code, localtime(self.start.replace(microsecond=0))
            ) if v)
        )

    class Meta:
        abstract = True


class InputRequestLog(InputRequestLogStrMixin, RequestLog):

    user_id = models.TextField(
        null=True,
        blank=True,
        db_index=True
    )
    ip = models.GenericIPAddressField(
        null=False,
        blank=False,
        db_index=True
    )
    view_slug = models.CharField(
        null=True,
        blank=True,
        db_index=True,
        max_length=255
    )
    related_objects = MultipleDBGenericManyToManyField()

    objects = BaseLogQuerySet.as_manager()

    class Meta:
        ordering = ('-start',)

    @cached_property
    def user(self):
        return get_user_model().objects.filter(pk=self.user_id).first()


class OutputRequestLog(OutputRequestLogStrMixin, RequestLog):

    related_objects = MultipleDBGenericManyToManyField()

    objects = BaseLogQuerySet.as_manager()

    class Meta:
        ordering = ('-start',)

    class SmartMeta:
        is_cleaned_pre_save = False


class CommandLog(CommandLogStrMixin, Log):
    """
    Represents a log of a command run.

    Attributes:
        start: Date and time when command was started.
        stop: Date and time when command finished.
        time: Command processing time in miliseconds.
        name: Name of the command.
        options: Arguments/options the command was run with.
        is_executed_from_command_line: Flag that indicates if command was run from the command line.
        output: Standard and error output of the command.
        is_successful: Flag that indicates if command finished successfully.
    """
    name = models.CharField(
        max_length=250,
        blank=False,
        null=False,
        editable=False,
        db_index=True
    )
    input = models.TextField(
        blank=False,
        null=False,
        editable=False
    )
    is_executed_from_command_line = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        editable=False
    )
    output = models.TextField(
        blank=True,
        null=True,
        editable=False
    )
    state = IntegerEnumField(
        null=False,
        blank=False,
        enum=CommandState,
        default=CommandState.ACTIVE,
        db_index=True
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        editable=False
    )
    related_objects = MultipleDBGenericManyToManyField()

    objects = BaseLogQuerySet.as_manager()

    class Meta:
        ordering = ('-start',)


class CeleryTaskInvocationLogManager(models.Manager):

    def filter_not_started(self):
        return self.filter(
            state__in={
                CeleryTaskInvocationLogState.WAITING,
                CeleryTaskInvocationLogState.TRIGGERED
            }
        )

    def filter_processing(self, related_objects=None, **kwargs):
        qs = self.filter(
            state__in={
                CeleryTaskInvocationLogState.ACTIVE,
                CeleryTaskInvocationLogState.WAITING,
                CeleryTaskInvocationLogState.TRIGGERED
            }
        ).filter(**kwargs)

        if related_objects:
            for related_object in related_objects:
                qs = qs.filter(
                    related_objects__object_id=related_object.pk,
                    related_objects__object_ct_id=ContentType.objects.get_for_model(related_object).pk
                )
        return qs


class CeleryTaskInvocationLog(CeleryTaskInvocationLogStrMixin, Log):

    celery_task_id = models.UUIDField(
        max_length=250,
        db_index=True,
        null=True,
        blank=True
    )
    name = models.CharField(
        null=False,
        blank=False,
        max_length=250,
        db_index=True
    )
    queue_name = models.CharField(
        null=True,
        blank=True,
        max_length=250
    )
    applied_at = models.DateTimeField(
        null=False,
        blank=False
    )
    triggered_at = models.DateTimeField(
        null=True,
        blank=True
    )
    is_unique = models.BooleanField()
    is_async = models.BooleanField()
    is_duplicate = models.BooleanField(
        null=True,
        blank=True
    )
    is_on_commit = models.BooleanField()
    input = models.TextField(
        blank=True,
        null=True,
        editable=False
    )
    task_args = models.JSONField(
        null=True,
        blank=True,
        editable=False,
        encoder=DjangoJSONEncoder
    )
    task_kwargs = models.JSONField(
        null=True,
        blank=True,
        editable=False,
        encoder=DjangoJSONEncoder
    )
    estimated_time_of_first_arrival = models.DateTimeField(
        null=True,
        blank=True
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )
    stale_at = models.DateTimeField(
        null=True,
        blank=True
    )
    state = IntegerEnumField(
        null=False,
        blank=False,
        enum=CeleryTaskInvocationLogState,
        default=CeleryTaskInvocationLogState.WAITING,
        db_index=True
    )

    related_objects = MultipleDBGenericManyToManyField()

    objects = CeleryTaskInvocationLogManager.from_queryset(BaseLogQuerySet)()

    class Meta:
        ordering = ('-start',)

    def __str__(self):
        return '{} ({})'.format(self.name, self.state.label)

    @property
    def runs(self):
        return CeleryTaskRunLog.objects.filter(celery_task_id=self.celery_task_id)

    @property
    def last_run(self):
        return CeleryTaskRunLog.objects.filter(celery_task_id=self.celery_task_id).first()

    @property
    def first_run(self):
        return CeleryTaskRunLog.objects.filter(celery_task_id=self.celery_task_id).last()


class CeleryTaskRunLog(CeleryTaskRunLogStrMixin, Log):

    celery_task_id = models.UUIDField(
        max_length=250,
        db_index=True,
        null=True,
        blank=True
    )
    name = models.CharField(
        null=False,
        blank=False,
        max_length=250,
        db_index=True
    )
    queue_name = models.CharField(
        null=True,
        blank=True,
        max_length=250
    )
    input = models.TextField(
        blank=True,
        null=True,
        editable=False
    )
    task_args = models.JSONField(
        null=True,
        blank=True,
        editable=False,
        encoder=DjangoJSONEncoder
    )
    task_kwargs = models.JSONField(
        null=True,
        blank=True,
        editable=False,
        encoder=DjangoJSONEncoder
    )
    state = IntegerEnumField(
        null=False,
        blank=False,
        enum=CeleryTaskRunLogState,
        default=CeleryTaskRunLogState.ACTIVE,
        db_index=True
    )
    result = models.JSONField(
        blank=True,
        null=True,
        editable=False,
        encoder=DjangoJSONEncoder
    )
    error_message = models.TextField(
        null=True,
        blank=True
    )
    output = models.TextField(
        blank=True,
        null=True,
        editable=False
    )
    retries = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
        default=0
    )
    estimated_time_of_next_retry = models.DateTimeField(
        null=True,
        blank=True
    )
    waiting_time = models.FloatField(
        null=True,
        blank=True
    )
    related_objects = MultipleDBGenericManyToManyField()

    objects = BaseLogQuerySet.as_manager()

    class Meta:
        ordering = ('-start',)

    def __str__(self):
        return '{} ({})'.format(self.name, self.get_state_display())

    def get_task_invocation_logs(self):
        return CeleryTaskInvocationLog.objects.filter(celery_task_id=self.celery_task_id)


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
    except ObjectDoesNotExist:
        return None


def get_log_key(log):
    logger_name = {v: k for k, v in logger_name_to_log_model.items()}[log.__class__]
    return '{}|{}'.format(logger_name, log.id)
