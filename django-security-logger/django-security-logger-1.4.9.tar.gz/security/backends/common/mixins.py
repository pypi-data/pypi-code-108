from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _l


class LogShortIdMixin:

    @property
    def short_id(self):
        return truncatechars(str(self.id), 8)


class LogStrMixin:

    VERBOSE_NAME = None

    def __str__(self):
        return '{} {}'.format(self.VERBOSE_NAME, self.short_id)


class InputRequestLogStrMixin(LogStrMixin):

    VERBOSE_NAME = _l('input request log')


class OutputRequestLogStrMixin(LogStrMixin):

    VERBOSE_NAME = _l('input request log')


class CommandLogStrMixin(LogStrMixin):

    VERBOSE_NAME = _l('command log')


class CeleryTaskInvocationLogStrMixin(LogStrMixin):

    VERBOSE_NAME = _l('celery task invocation log')


class CeleryTaskRunLogStrMixin(LogStrMixin):

    VERBOSE_NAME = _l('celery task run log')
