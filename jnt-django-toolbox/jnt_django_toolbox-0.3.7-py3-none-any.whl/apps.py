from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    """App config."""

    name = "jnt_django_toolbox"
    verbose_name = "Django toolbox"
    default = True
