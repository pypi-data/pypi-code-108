import operator
from typing import Tuple, Iterable, List, Set

from django.db import models

from vtb_django_utils.model_versions.utils.consts import REL_VERSION_FIELD_END, REL_VERSION_PATTERN_FIELD_END
from vtb_django_utils.utils.db import get_model_field_names


def get_all_available_major_version(versions: Iterable[List[int]]) -> List[Tuple[str, str]]:
    all_version: Set[tuple] = set()
    for version in versions:
        all_version.add((f'{version[0]}.', f'{version[0]}.x.x'))
        all_version.add((f'{version[0]}.{version[1]}.', f'{version[0]}.{version[1]}.x'))
    return sorted((version for version in all_version), key=operator.itemgetter(1))


def get_rel_model_version_from_dict(instance_dict: dict, rel_field: models.Field):
    """ Возвращает инстанс версии с учетом выбранной версии и шаблона """
    rel_field_name = rel_field.name
    if rel_version_model_id := instance_dict.get(f'{rel_field_name}_id', instance_dict.get(rel_field_name)):
        rel_instance = rel_field.related_model.objects.get(pk=rel_version_model_id)
        rel_version = instance_dict.get(f'{rel_field_name}{REL_VERSION_FIELD_END}')
        rel_version_pattern = instance_dict.get(f'{rel_field_name}{REL_VERSION_PATTERN_FIELD_END}')
        return rel_instance.get_version_by_pattern(rel_version or rel_version_pattern)
    return None


def get_rel_model_version_str_from_dict(instance_dict: dict, rel_field: models.Field):
    """ Возвращает инстанс версии с учетом выбранной версии и шаблона """
    if rel_version_instance := get_rel_model_version_from_dict(instance_dict, rel_field):
        return rel_version_instance.version
    return ''


def get_rel_versioned_field_names(model_class) -> set:
    """ Возвращает имена полей связанной версионной модели """
    def _get_fields(pattern):
        return set([f.replace(pattern, '') for f in field_names if f.endswith(pattern)])

    field_names = get_model_field_names(model_class)
    rel_fields = set(_get_fields(REL_VERSION_FIELD_END)) & set(_get_fields(REL_VERSION_PATTERN_FIELD_END))
    return rel_fields
