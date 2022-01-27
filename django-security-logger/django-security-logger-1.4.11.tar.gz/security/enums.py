from django.utils.translation import ugettext_lazy as _

from enum import Enum

from enumfields import Choice, IntegerChoicesEnum


class RequestLogState(IntegerChoicesEnum):

    INCOMPLETE = Choice(0, _('Incomplete'))
    DEBUG = Choice(10, _('Debug'))
    INFO = Choice(20, _('Info'))
    WARNING = Choice(30, _('Warning'))
    ERROR = Choice(40, _('Error'))


class CommandState(IntegerChoicesEnum):

    ACTIVE = Choice(1, _('Active'))
    SUCCEEDED = Choice(2, _('Succeeded'))
    FAILED = Choice(3, _('Failed'))


class CeleryTaskInvocationLogState(IntegerChoicesEnum):

    WAITING = Choice(1, _('Waiting'))
    TRIGGERED = Choice(7, _('Triggered'))
    ACTIVE = Choice(2, _('Active'))
    SUCCEEDED = Choice(3, _('Succeeded'))
    FAILED = Choice(4, _('Failed'))
    EXPIRED = Choice(6, _('Expired'))
    TIMEOUT = Choice(8, _('Timeout'))
    IGNORED = Choice(9, _('Ignored'))


class CeleryTaskRunLogState(IntegerChoicesEnum):

    ACTIVE = Choice(1, _('Active'))
    SUCCEEDED = Choice(2, _('Succeeded'))
    FAILED = Choice(3, _('Failed'))
    RETRIED = Choice(4, _('Retried'))
    EXPIRED = Choice(5, _('Expired'))


class InputRequestSlug(str, Enum):

    UNSUCCESSFUL_LOGIN_REQUEST = 'UNSUCCESSFUL_LOGIN_REQUEST'
    SUCCESSFUL_LOGIN_REQUEST = 'SUCCESSFUL_LOGIN_REQUEST'
    UNSUCCESSFUL_2FA_CODE_VERIFICATION_REQUEST = 'UNSUCCESSFUL_2FA_CODE_VERIFICATION_REQUEST'
    SUCCESSFUL_2FA_CODE_VERIFICATION_REQUEST = 'SUCCESSFUL_2FA_CODE_VERIFICATION_REQUEST'


class LoggerName(str, Enum):

    INPUT_REQUEST = 'input-request',
    OUTPUT_REQUEST = 'output-request',
    COMMAND = 'command',
    CELERY_TASK_INVOCATION = 'celery-task-invocation'
    CELERY_TASK_RUN = 'celery-task-run'
