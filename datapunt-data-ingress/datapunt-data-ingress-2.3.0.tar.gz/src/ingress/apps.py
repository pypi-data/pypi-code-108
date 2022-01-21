from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

from ingress.settings import app_settings


class IngressConfig(AppConfig):
    name = "ingress"

    def ready(self):
        auth_settings = (
            'PERMISSION_CLASSES',
            'AUTHENTICATION_CLASSES',
            'DISABLE_ALL_AUTH_PERMISSION_CHECKS',
        )
        if not any(
            [getattr(app_settings, auth_setting) for auth_setting in auth_settings]
        ):
            raise ImproperlyConfigured(
                f"At lease one of {', '.join(auth_settings)} "
                f"must be set in the settings"
            )

        super().ready()
