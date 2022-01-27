from __future__ import annotations

import json
from copy import copy
from functools import wraps
from typing import Optional, List, Tuple, Type, Union

from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import JSONField, Func, F, Value
from django.forms import model_to_dict
from django_lifecycle import hook, BEFORE_SAVE

from vtb_django_utils.user_info.info import get_user_info
from vtb_django_utils.utils.class_factory import class_factory
from vtb_django_utils.utils.db import CreatedMixin, get_rel_model_fields
from vtb_django_utils.utils.diff import get_objs_diff
from vtb_django_utils.utils.jsons import get_json_hash, JSONEncoder
from .utils.consts import START_VERSION, THERE_IS_NO_VERSION_DATA, DOES_NOT_EXIST_VERSION, REL_VERSION_FIELD_END, \
    REL_VERSION_PATTERN_FIELD_END, VERSION_DELIMITER, ERR_VERSIONED_OBJ_NOT_SELECTED, \
    ERR_VERSIONED_OBJ_DONT_MATCH_SELECTED_VERSION, ERR_SELECTED_VERSION_AND_PATTERN, ERR_WRONG_VERSION_PATTERN_FORMAT, \
    VERSION_PATTERN_REGEX, VERSION_MODEL_SUFFIX, RE_VERSION, ERR_VERSION_FORMAT, MAX_VERSION_PART, \
    ERR_VERSION_COUNTER_FULL
from .utils.models import get_rel_versioned_field_names
from .utils.regex import version_regex
from .utils.strings import int_arr_to_str, str_to_int_arr
from ..utils.exceptions import VersionException


class VersionModel(CreatedMixin, models.Model):
    """ Базовый класс для версий какой-либо модели """
    user = JSONField(default=dict, blank=True)
    json = JSONField(default=dict, blank=True)
    hash = models.TextField()
    version_arr = ArrayField(models.PositiveSmallIntegerField(), max_length=3, default=list, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        self._validate_version_range()

    @hook(BEFORE_SAVE)
    def _validate_version_range(self):
        if not RE_VERSION.match(int_arr_to_str(self.version_arr)):
            raise ValidationError(ERR_VERSION_FORMAT.format(self.version_arr))

    @property
    def version(self) -> str:
        """ Возвращает версию в виде строки """
        return int_arr_to_str(self.version_arr)

    @property
    def changed_by_user(self) -> str:
        """ Имя пользователя, создавшего версию """
        # noinspection PyUnresolvedReferences
        return self.user.get('username', '')


class ModelJsonMixin:
    """ Добавляет метод получения джейсона модели """
    @property
    def json(self) -> dict:
        rel_field_names = get_rel_model_fields(self.__class__)
        result = model_to_dict(self, exclude=rel_field_names)
        # noinspection PyUnresolvedReferences
        result['id'] = self.id
        # связанные модели
        for rel_field_name in rel_field_names:
            rel_obj = getattr(self, rel_field_name)
            if rel_field_name.endswith(REL_VERSION_FIELD_END):
                # Поле для версии модели заменяется на значение версии
                result[f'{rel_field_name}'] = rel_obj.version if rel_obj else ''
            else:
                result[f'{rel_field_name}_id'] = rel_obj.pk if rel_obj else None
        result = json.loads(json.dumps(result, sort_keys=True, cls=JSONEncoder))
        return result


class ModelVersionedRelFieldsInfoMixin:
    """ Миксин для получения информации о полях связанной версионной модели """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_versioned_fields = get_rel_versioned_field_names(self.__class__)


class ModelWithVersionedRelations(ModelVersionedRelFieldsInfoMixin, ModelJsonMixin, models.Model):
    """ Миксин для работы со связанными версионными моделями (например граф в экшене) """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_name = self.__class__.__name__

    def clean(self):
        super().clean()
        self._validate_rel_version()

    @hook(BEFORE_SAVE)
    def _validate_rel_version(self):
        self.validation_versioned_instance_not_selected()
        self.validation_version_pattern_format()
        self.validation_versioned_instance_not_natch_version()
        self.validation_select_version_and_pattern()

    def validation_versioned_instance_not_selected(self):
        """ Проверка что если задана ее версия или шаблон, то модель с версией тоже выбрана """
        for rel_field in self.rel_versioned_fields:
            versioned_instance_id = getattr(self, f'{rel_field}_id')
            version = getattr(self, f'{rel_field}{REL_VERSION_FIELD_END}')
            version_pattern = getattr(self, f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}')
            if not versioned_instance_id and (version or version_pattern):
                raise ValidationError(ERR_VERSIONED_OBJ_NOT_SELECTED.format(rel_field.capitalize()))

    def validation_version_pattern_format(self):
        """ Проверяет формат паттерна версии """
        for rel_field in self.rel_versioned_fields:
            version_pattern = getattr(self, f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}')
            if version_pattern and not VERSION_PATTERN_REGEX.match(version_pattern):
                raise ValidationError(ERR_WRONG_VERSION_PATTERN_FORMAT + f' for {str(self)}')

    def validation_versioned_instance_not_natch_version(self):
        """ Проверка что выбраная модель с версией и выбранная версия соответствуют """
        for rel_field in self.rel_versioned_fields:
            versioned_instance = getattr(self, f'{rel_field}')
            version = getattr(self, f'{rel_field}{REL_VERSION_FIELD_END}')
            if versioned_instance and version and not versioned_instance.versions.filter(id=version.id).exists():
                raise ValidationError(ERR_VERSIONED_OBJ_DONT_MATCH_SELECTED_VERSION.format(
                    str(version), self.class_name, str(getattr(self, f'{rel_field}'))
                ))

    def validation_select_version_and_pattern(self):
        """ Нельзя выбрать версию и шаблон версии одновременно """
        for rel_field in self.rel_versioned_fields:
            version = getattr(self, f'{rel_field}{REL_VERSION_FIELD_END}')
            version_pattern = getattr(self, f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}')
            if version and version_pattern:
                raise ValidationError(ERR_SELECTED_VERSION_AND_PATTERN.format(self.class_name))

    def get_rel_model_version(self, rel_field_name: str) -> Optional[VersionModel]:
        """ Возвращает инстанс версии с учетом выбранной версии и шаблона """
        if rel_version_model := getattr(self, rel_field_name):
            rel_version_instance = getattr(self, f'{rel_field_name}{REL_VERSION_FIELD_END}')
            rel_version_pattern = getattr(self, f'{rel_field_name}{REL_VERSION_PATTERN_FIELD_END}')
            return rel_version_model.get_version_by_pattern(rel_version_instance or rel_version_pattern)
        return None

    def get_rel_model_version_str(self, rel_field_name: str) -> str:
        """ Возвращает строку версии с учетом выбранной версии и шаблона """
        if rel_version_instance := self.get_rel_model_version(rel_field_name):
            return rel_version_instance.version
        return ''


def version_info_cache(func):
    @wraps(func)
    def __wrap(self, *args, **kwargs):
        var_name = f'_{func.__name__}'
        values_store = self._get_obj_ver_cache()
        if not (result := values_store.get(var_name)):
            result = values_store[var_name] = func(self, *args, **kwargs)
            self._set_obj_ver_cache(values_store)
        return result
    return __wrap


class VersionedModelMixin(ModelVersionedRelFieldsInfoMixin, ModelJsonMixin):
    """ Добавляет методы для работы с версиями модели """
    @property
    def versions_set(self):
        """ Возвращает set связанной модели с версиями по related_name """
        return getattr(self, 'versions')

    @property
    def hash(self) -> str:
        """ Возвращает хеш json  """
        return get_json_hash(self.json)

    def get_version_by_pattern(self, version_pattern_attr: Union[int, str, VersionModel] = None) -> VersionModel:
        """ Возвращает инстанс версии модели по шаблону """
        if not version_pattern_attr:
            return self.last_version

        if isinstance(version_pattern_attr, VersionModel):
            return version_pattern_attr

        if isinstance(version_pattern_attr, int):
            return self.versions_set.get(pk=version_pattern_attr)

        if len([s for s in version_pattern_attr.split(VERSION_DELIMITER) if s]) < 3:
            # это паттерн
            version_instance = self.versions_set.annotate(
                exact_version=Func(F('version_arr'), Value(VERSION_DELIMITER), function='array_to_string')
            ).filter(
                exact_version__regex=version_regex(version_pattern_attr)
            ).order_by('-version_arr').first()
        else:
            # это строка
            try:
                version_instance = self.versions_set.get(version_arr=str_to_int_arr(version_pattern_attr))
            except self.versions_set.model.DoesNotExist:
                # noinspection PyUnresolvedReferences
                raise VersionException(f'Версия {version_pattern_attr} для {str(self)} id={self.pk} не существует')

        return version_instance

    @property
    @version_info_cache
    def version_list(self) -> List[str]:
        """ Возвращает список версий в виде строк """
        return self.versions_set.annotate(
            exact_version=Func(F('version_arr'), Value(VERSION_DELIMITER), function='array_to_string')
        ).values_list('exact_version', flat=True)

    @property
    @version_info_cache
    def last_version(self) -> Optional[VersionModel]:
        """ Возвращает инстанс последней версии """
        return self.versions_set.order_by('-version_arr').first()

    @property
    def is_version_changed(self) -> bool:
        """ Возвращает признак изменения json модели по сравнению с посделней сохраненной версией """
        if self.last_version and self.hash == self.last_version.hash:
            return False
        return True

    @property
    def next_version_str(self) -> str:
        """ Возвращает строку со следующей версией, инкрементированной по минору """
        last_version = self.last_version
        if last_version and last_version.version_arr:
            # noinspection PyTypeChecker
            version_arr = list(last_version.version_arr)
            is_overflow = True
            last_index = len(version_arr) - 1
            for i, part in enumerate(version_arr[::-1]):
                if part < MAX_VERSION_PART:
                    version_arr[last_index - i] += 1
                    is_overflow = False
                    break
                else:
                    # noinspection PyUnresolvedReferences
                    version_arr[last_index - i] = 0
            if is_overflow:
                raise ValidationError(ERR_VERSION_COUNTER_FULL.format(last_version.version_arr))
            return int_arr_to_str(version_arr)
        else:
            return START_VERSION

    def add_version_for_rel_versioned_obj(self, model_version_json):
        """ Добавляет информацию о версиях связанных моделей """
        for rel_field in self.rel_versioned_fields:
            obj_version = getattr(self, f'{rel_field}{REL_VERSION_FIELD_END}')
            model_version_json[f'{rel_field}{REL_VERSION_FIELD_END}'] = obj_version.version if obj_version else ''

    def get_json_by_version(self, version_or_pattern: Union[int, str, VersionModel] = None,
                            json_field_name: str = 'json',
                            compare_with_version: str = None) -> dict:
        """ Возвращает json версии по строке версии (или паттерну) """
        if version_or_pattern:
            version_instance = self.get_version_by_pattern(version_pattern_attr=version_or_pattern)
        else:
            version_instance = self.last_version

        if version_instance:
            model_version_json = copy(getattr(version_instance, json_field_name, {}))
            if not model_version_json:
                model_version_json['error'] = f'{THERE_IS_NO_VERSION_DATA} {self.__class__.__name__}:{version_instance}'
            model_version_json['version'] = version_instance.version
            model_version_json['version_create_dt'] = version_instance.create_dt
            model_version_json['version_changed_by_user'] = version_instance.changed_by_user
            # добавляем разницу с указанной версией (если заказано)
            if compare_with_version:
                json_diff = {'compare_with_version': compare_with_version}
                try:
                    compare_version_instance = self.versions_set.get(version_arr=str_to_int_arr(compare_with_version))
                except self.versions_set.model.DoesNotExist:
                    json_diff['err'] = DOES_NOT_EXIST_VERSION.format(compare_with_version)
                else:
                    origin_version_json = getattr(version_instance, json_field_name)
                    compare_version_json = getattr(compare_version_instance, json_field_name)
                    json_diff['diff'] = get_objs_diff(compare_version_json or type(compare_version_json)(),
                                                      origin_version_json)
                    json_diff['changed_by_user'] = compare_version_instance.changed_by_user
                model_version_json['version_diff'] = json_diff
        else:
            model_version_json = {}

        return model_version_json

    @transaction.atomic
    def create_or_update_version(self, version_str: str = None) -> Tuple[bool, VersionModel]:
        """ Создает или обновляет версию """
        # Удаляем закешированные свойства
        self.clear_prefetch_cache('versions')

        version = version_str or self.next_version_str
        if not RE_VERSION.match(version):
            raise ValidationError(ERR_VERSION_FORMAT.format(version))

        model_version, is_created = self.versions_set.get_or_create(
            version_arr=str_to_int_arr(version),
        )
        if not is_created:
            raise ValidationError(f'Версия {version} для {str(self)} уже существует')

        # Удаляем закешированные свойства
        self.clear_prefetch_cache('versions')

        model_version.user = get_user_info()
        model_version = self._patch_model_version(model_version)
        model_version.save()

        return is_created, model_version

    def _patch_model_version(self, model_version: VersionModel) -> VersionModel:
        """ Модификация полей версии """
        model_version.json = self.json
        model_version.hash = self.hash
        return model_version

    @property
    def _cache_key(self) -> str:
        # noinspection PyUnresolvedReferences
        return f'ver_{self.__class__.__name__}.{self.pk}'

    def _get_obj_ver_cache(self) -> dict:
        return cache.get(self._cache_key) or {}

    def _set_obj_ver_cache(self, cache_value: dict):
        cache.set(self._cache_key, cache_value)

    def _del_obj_ver_cache(self):
        if self._cache_key in cache:
            cache.delete(self._cache_key)

    def clear_prefetch_cache(self, cache_name: str):
        if hasattr(self, '_prefetched_objects_cache'):
            self._prefetched_objects_cache.pop(cache_name, None)
        self._del_obj_ver_cache()


def create_version_model_class(
        module_name: str, model_name: str, version_parent_model: Type[VersionModel],
        model_mixins: Tuple[Type[models.Model]] = None) -> VersionModel:
    """ Фабрика создании модели с версиями """
    lower_name = model_name.lower()
    capitalize_name = model_name.capitalize()
    meta_fields = dict(
        verbose_name=f'{lower_name} version',
        verbose_name_plural=f'{lower_name} versions',
        unique_together=(f'{lower_name}_id', 'version_arr'),
        ordering=(f'{lower_name}_id', 'version_arr'),
    )

    # create class Meta
    class_meta = class_factory(module_name, 'Meta', (version_parent_model.Meta,), {})
    for k, v in meta_fields.items():
        setattr(class_meta, k, v)

    # create class VersionModel
    parents = (*model_mixins, version_parent_model) if model_mixins else (version_parent_model,)
    version_class = class_factory(module_name, f'{capitalize_name}{VERSION_MODEL_SUFFIX}', parents, {
        lower_name: models.ForeignKey(capitalize_name, related_name='versions', on_delete=models.CASCADE),
        'Meta': class_meta,
    })
    version_class.__str__ = lambda self: f'{getattr(self, lower_name)}:{self.version}'

    return version_class


def is_instance_versioned(instance):
    return isinstance(instance, VersionedModelMixin)
