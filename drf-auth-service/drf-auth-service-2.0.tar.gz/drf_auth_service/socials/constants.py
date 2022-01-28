from django.db import models
from django.utils.translation import gettext as _


class DeviceTypes(models.TextChoices):
    ANDROID = 'android', _('Android')
    IOS = 'ios', _('Ios')
    WEB = 'web', _('Web')
