from django.apps import AppConfig
from willow.registry import registry


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mycarehub.content"

    def ready(self):
        import rustface.willow  # noqa

        registry.register_plugin(rustface.willow)
