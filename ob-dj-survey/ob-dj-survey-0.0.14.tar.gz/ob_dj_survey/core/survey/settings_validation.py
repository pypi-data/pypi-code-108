from django.apps import apps
from django.core.checks import Error

REQUIRED_INSTALLED_APPS = [
    "rest_framework",
]

REQUIRED_DEPENDENCIES = [
    "celery>=5",
]


def required_dependencies(app_configs, **kwargs):
    return []


def required_installed_apps(app_configs, **kwargs):
    return [
        Error(f"{app} is required in INSTALLED_APPS")
        for app in REQUIRED_INSTALLED_APPS
        if not apps.is_installed(app)
    ]


def required_settings(app_configs, **kwargs):
    return []
