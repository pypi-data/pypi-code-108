from django.apps import AppConfig

from . import __version__


class StructureTimersConfig(AppConfig):
    name = "structuretimers"
    label = "structuretimers"
    verbose_name = f"Structure Timers v{__version__}"
