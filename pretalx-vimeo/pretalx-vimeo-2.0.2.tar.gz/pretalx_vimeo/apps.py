from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PluginApp(AppConfig):
    name = "pretalx_vimeo"
    verbose_name = "Vimeo integration"

    class PretalxPluginMeta:
        name = gettext_lazy("Vimeo integration")
        author = "Tobias Kunze"
        description = gettext_lazy(
            "Embed Vimeo videos as session recordings, and retrieve them via an API."
        )
        visible = True
        version = "2.0.2"

    def ready(self):
        from . import signals  # NOQA
