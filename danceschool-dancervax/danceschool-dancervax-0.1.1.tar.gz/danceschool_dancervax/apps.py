# Give this app a custom verbose name to avoid confusion
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DanceSchoolDancerVaxAppConfig(AppConfig):
    name = 'danceschool_dancervax'
    verbose_name = _('DancerVax Integration')

    def ready(self):
        # Ensure that a persistent session linking to DancerVax is loaded
        from .session import dancervax_session

        # Ensure that signal handlers are loaded
        from . import handlers
