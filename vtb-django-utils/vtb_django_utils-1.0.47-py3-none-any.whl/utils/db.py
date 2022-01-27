from functools import lru_cache
from typing import List, Optional, Union, Type

from django.db import models
from django.utils import timezone


class CreatedMixin(models.Model):
    create_dt = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        abstract = True
        ordering = ('create_dt',)


@lru_cache
def get_model_fields(model_class, exclude: Union[tuple, list] = None) -> List[models.Field]:
    """ Возвращает список полей модели БД """
    exclude_set = set(exclude or [])
    # noinspection PyProtectedMember
    return [f for f in model_class._meta.fields if f.name not in exclude_set]


@lru_cache
def get_model_field_names(model_class, exclude: Union[tuple, list] = None) -> List[str]:
    """ Возвращает список полей модели БД """
    exclude_set = set(exclude or [])
    # noinspection PyProtectedMember
    return [f.name for f in model_class._meta.fields if f.name not in exclude_set]


@lru_cache
def get_rel_model_fields(model_class, exclude: Union[tuple, list] = None) -> List[str]:
    """ Возвращает список реляционных полей модели БД """
    exclude_set = set(exclude or [])
    # noinspection PyProtectedMember
    return [f.name for f in model_class._meta.fields
            if f.name not in exclude_set and getattr(f, 'foreign_related_fields', None)]


def create_model_from_dict(model_class, data: dict, ignore_fields: Optional[Union[list, tuple]] = None):
    """ Создает экземпляр модели в БД из словаря """
    db_field_names = set(get_model_field_names(model_class))
    ignore_fields = ignore_fields or []
    return model_class.objects.create(**{
        k: v for k, v in data.items()
        if k in db_field_names and k not in ignore_fields}
    )


@lru_cache
def not_required_model_fields(model_class: Type[models.Model]) -> list:
    """ Возвращает необязательные поля модели """
    # noinspection PyProtectedMember,PyUnresolvedReferences
    return [field.attname for field in model_class._meta.fields if field.null]
