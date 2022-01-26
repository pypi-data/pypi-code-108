from django.apps import AppConfig as DjangoAppConfig
from django.contrib.admin.apps import AdminConfig as DjangoAdminConfig
from django.core.management.color import color_style

style = color_style()


class AdminConfig(DjangoAdminConfig):
    default_site = "mocca_edc.admin.AdminSite"


class AppConfig(DjangoAppConfig):
    name = "mocca_edc"
    verbose_name = "MOCCA Edc"
