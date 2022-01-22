# Django
from django.apps import AppConfig

from . import __version__


class TnntTemplatesConfig(AppConfig):
    name = "tnnt_templates"
    label = "tnnt_templates"
    verbose_name = f"Alliance Auth Templates v{__version__}"
