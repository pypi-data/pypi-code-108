from django.utils.module_loading import import_string
from django.conf import settings


SIMPLE_PERMS_MODULE_NAME = getattr(settings, 'SIMPLE_PERMS_MODULE_NAME', 'perms')
SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION = getattr(settings, 'SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION', None)
if SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION:
    SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION = import_string(SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION)
else:
    SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION = lambda user, obj, perm: False  # noqa
