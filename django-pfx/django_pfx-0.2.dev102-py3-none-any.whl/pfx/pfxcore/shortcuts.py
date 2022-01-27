
import logging
import re

from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def f(tmpl, **kwargs):
    return tmpl.format(**kwargs)


def get_object(queryset, **kwargs):
    from .exceptions import ModelNotFoundAPIError
    try:
        return queryset.get(**kwargs)
    except ObjectDoesNotExist:
        raise ModelNotFoundAPIError(queryset.model)


def get_pk(obj):
    if isinstance(obj, dict) and 'pk' in obj:
        return obj['pk']
    return obj


RE_FALSE = re.compile(r'^(0|false|)$', re.IGNORECASE)


def parse_bool(value):
    return value and not RE_FALSE.match(value)
