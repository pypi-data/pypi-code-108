from django.apps import AppConfig


class OpcalendarConfig(AppConfig):
    name = "opcalendar"

    def ready(self):
        import opcalendar.signals  # noqa: F401
