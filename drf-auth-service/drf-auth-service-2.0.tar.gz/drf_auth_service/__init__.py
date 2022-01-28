from django.apps import AppConfig


class AuthServiceConfig(AppConfig):
    name = 'drf_auth_service'
    verbose_name = "AuthService"

    def ready(self):
        import drf_auth_service.signals  # noqa


default_app_config = 'drf_auth_service.AuthServiceConfig'
