from django.apps import AppConfig
from django.core.checks import register
from django.utils.translation import gettext_lazy as _

from ob_dj_survey.core.survey import settings_validation


class SurveyConfig(AppConfig):
    name = "ob_dj_survey.core.survey"
    verbose_name = _("Survey")

    def ready(self):
        register(settings_validation.required_settings)
        register(settings_validation.required_dependencies)
        register(settings_validation.required_installed_apps)
