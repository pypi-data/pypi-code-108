from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

__all__ = ('ActionsTrackerConfig',)


class ActionsTrackerConfig(AppConfig):
    name = 'pxd_actions_tracker'
    verbose_name = pgettext_lazy('pxd-actions-tracker', 'Actions tracker')
