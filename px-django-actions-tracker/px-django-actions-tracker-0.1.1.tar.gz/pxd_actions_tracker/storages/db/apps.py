from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

__all__ = ('DBActionsTrackerConfig',)


class DBActionsTrackerConfig(AppConfig):
    name = 'pxd_actions_tracker.storages.db'
    label = 'pxd_actions_tracker_storages_db'
    verbose_name = pgettext_lazy('pxd-actions-tracker', 'Actions tracker: Database')
