from abc import ABCMeta
from functools import wraps

from django.db import transaction
from rest_framework import serializers

from vtb_django_utils.model_versions.utils.consts import REL_VERSION_FIELD_END, REL_VERSION_CALCULATED_FIELD_END
from vtb_django_utils.model_versions.utils.models import get_rel_versioned_field_names
from vtb_django_utils.model_versions.utils.strings import str_to_int_arr
from vtb_django_utils.utils.db import get_model_fields


def create_version_decorator(func):
    @wraps(func)
    def __wrap(self, *args, **kwargs):
        validated_data = kwargs.get('validated_data', None) or args[-1]
        version = validated_data.pop('version', None)
        instance = func(self, *args, **kwargs)
        # Некоторым сущностям нужно создавать версию, после добавления реляций
        if getattr(self, 'is_create_version', True):
            # Апдейтим версию version или создаем новую, если ее нет. Если version не указана, то создаем следующую
            _, model_version = instance.create_or_update_version(version)
            instance.version = model_version.version
        return instance

    return __wrap


class VersionedModelSerializer(serializers.ModelSerializer):
    __metaclass__ = ABCMeta
    version = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')

    class Meta:
        model = None

    @transaction.atomic()
    @create_version_decorator
    def create(self, validated_data):
        return super().create(validated_data)

    @transaction.atomic()
    @create_version_decorator
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def to_internal_value(self, data):
        model = self.Meta.model
        rel_field_names = get_rel_versioned_field_names(model)
        rel_fields = [f for f in get_model_fields(model) if f.name in rel_field_names]
        data_patch = {}

        # версии связанных моделей
        for rel_field in rel_fields:
            # id связанной модели
            rel_field_id_name = f'{rel_field.name}_id'
            if rel_field_id_name in data:
                if rel_field_id := data.get(rel_field_id_name):
                    data_patch[rel_field_id_name] = rel_field_id
                else:
                    data_patch[rel_field_id_name] = None
            else:
                rel_field_id = getattr(self.instance, rel_field_id_name) if self.instance else None

            # id версии
            version_field_name = f'{rel_field.name}{REL_VERSION_FIELD_END}'
            version_field_value = data.pop(version_field_name, None)
            version_field_id_name = f'{version_field_name}_id'
            if rel_field_id and version_field_value:
                version_model_class = rel_field.related_model.versions.rel.related_model
                version_instance = version_model_class.objects.get(**{
                    rel_field_id_name: rel_field_id,
                    'version_arr': str_to_int_arr(version_field_value),
                })
                data_patch[version_field_id_name] = version_instance.id
            else:
                data_patch[version_field_id_name] = None

        result = super(VersionedModelSerializer, self).to_internal_value(data)
        result.update(data_patch)
        return result

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if not (last_version := getattr(instance, 'last_version_query', '')):
            if instance.last_version:
                last_version = instance.last_version.version
            else:
                last_version = ''
        representation['last_version'] = last_version

        representation['version_list'] = getattr(instance, 'version_list_query', []) or instance.version_list

        # версия основной модели
        version = ''
        if not (request and (version := request.query_params.get('version', ''))):
            if not (version := representation.get('last_version')):
                if last_version := instance.last_version:
                    version = last_version.version
        representation['version'] = version

        model = instance.__class__
        rel_field_names = get_rel_versioned_field_names(model)
        # версии связанных моделей
        for field_name in rel_field_names:
            calc_field = f'{field_name}{REL_VERSION_CALCULATED_FIELD_END}'
            representation[calc_field] = self._get_version_calculated_str(instance, field_name)
            version_field = f'{field_name}{REL_VERSION_FIELD_END}'
            representation[version_field] = self._get_version_str(instance, field_name)
            field_id = f'{field_name}_id'
            representation[field_id] = getattr(instance, field_id)

        return representation

    @staticmethod
    def _get_version_str(instance, field_name: str) -> str:
        """ Возврашает строку с версией связанной модели (если выбрана версия) """
        # аннотированное значение из queryset
        if version_value := getattr(instance, f'{field_name}{REL_VERSION_FIELD_END}_query', None):
            return version_value
        # этот случай - если инстанс получен без аннотирования queryset
        if version_instance := getattr(instance, f'{field_name}{REL_VERSION_FIELD_END}'):
            return version_instance.version
        # нет реляции - нет значения
        return ''

    @staticmethod
    def _get_version_calculated_str(instance, field_name) -> str:
        """ Считает calculated версию для связанной модели """
        # аннотированное значение из queryset
        if version_calc_value := getattr(instance, f'{field_name}{REL_VERSION_CALCULATED_FIELD_END}_query', None):
            return version_calc_value
        # нет реляции - нет значения
        if not getattr(instance, field_name):
            return ''
        # этот случай - либо инстанс получен без аннотирования queryset, либо это паттерн версии
        return instance.get_rel_model_version_str(field_name)
