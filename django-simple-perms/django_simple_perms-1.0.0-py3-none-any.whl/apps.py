from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules
from .settings import SIMPLE_PERMS_MODULE_NAME


class SimplePermsConfig(AppConfig):
    name = 'simple_perms'
    verbose_name = 'Simple perms'

    def ready(self):
        autodiscover_modules(SIMPLE_PERMS_MODULE_NAME)
