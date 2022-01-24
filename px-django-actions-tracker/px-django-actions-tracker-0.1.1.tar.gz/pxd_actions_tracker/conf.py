from typing import Callable, Set
from px_settings.contrib.django import settings as s
from dataclasses import dataclass, field
from functools import lru_cache
from django.utils.module_loading import import_string

from .const import LogOperate


__all__ = 'NAME', 'Settings', 'settings',

NAME = 'PXD_ACTIONS_TRACKER'
cached_import = lru_cache(import_string)


@s(NAME)
@dataclass
class Settings:
    OPERATE: LogOperate = LogOperate.STRAIGHT
    SAVER: str = 'pxd_actions_tracker.storages.db.storage.save'
    SENSITIVE_FIELDS: Set[str] = field(default_factory=lambda: {
        'api',
        'token',
        'key',
        'secret',
        'password',
        'signature',
        'authorization',
    })
    SENSITIVE_PLACEHOLDER: str = '*******'

    def get_saver(self) -> Callable:
        return cached_import(self.SAVER)


settings = Settings()
