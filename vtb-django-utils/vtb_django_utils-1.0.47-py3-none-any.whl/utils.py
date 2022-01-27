from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_settings(attr_name, *args) -> Any:
    """
    Загрузка атрибута из django settings.
    @param attr_name: Наименование атрибута
    @return:
    """
    try:
        if args:
            return getattr(settings, attr_name, args[0])
        return getattr(settings, attr_name)
    except AttributeError:
        raise ImproperlyConfigured(f'Setting {attr_name} not found.')
