# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractproperty
from collections import Mapping
from collections import MutableMapping
from collections import defaultdict
from collections import namedtuple
from datetime import date
from datetime import datetime
from functools import partial
from uuid import UUID

from six import iteritems
from six import iterkeys
from six import text_type
from six import with_metaclass

from m3_gar_client.constants import GAR_LEVELS


FieldDescriptor = namedtuple('FieldDescriptor', [
    'data_type',
    'required',
    'description',
])


class ReadOnlyAttribute(object):

    def __init__(self, name, doc=None):
        self._name = name
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        return obj.__dict__[self._name] if obj else self

    def __set__(self, obj, value):
        raise AttributeError('{} is read only attribute'.format(self._name))

    def __delete__(self, obj):
        raise AttributeError('{} is read only attribute'.format(self._name))


class ObjectMeta(ABCMeta):

    def __new__(mcs, name, bases, namespace, **kwargs):  # @NoSelf
        cls = ABCMeta.__new__(mcs, name, bases, namespace)

        fields = namespace['fields']
        if isinstance(fields, dict):
            for field_name, field_descriptor in iteritems(fields):
                setattr(cls, field_name, ReadOnlyAttribute(
                    name=field_name,
                    doc=field_descriptor.description,
                ))

        return cls


class ObjectBase(with_metaclass(ObjectMeta, object)):
    """
    Базовый класс для объектов ГАР.
    Обеспечивает неизменяемость данных (объекты только для чтения).
    """

    @abstractproperty
    def fields(self):
        """Описание полей объекта."""

    def __hash__(self):
        return hash(self.id)  # pylint: disable=no-member

    def __init__(self, **kwargs):
        for field_name, field_descriptor in iteritems(self.fields):
            if field_descriptor.required:
                if field_name in kwargs:
                    field_value = kwargs[field_name]
                else:
                    raise TypeError('argument {} is required'.format(field_name))
            else:
                field_value = kwargs.get(field_name, None)

            if field_value and field_descriptor.data_type:
                try:
                    field_value = field_descriptor.data_type(field_value)
                except ValueError:
                    raise ValueError('{} = {}'.format(field_name, field_value))

            self.__dict__[field_name] = field_value


# dict в списке базовых классов нужен для правильной обработки данных в M3.
class ObjectDictAdapter(Mapping, dict):
    """
    Адаптер для объектов ГАР, преобразующий их к словарям.
    """

    def __init__(self, obj):  # pylint: disable=super-init-not-called
        """Инициализация экземпляра класса.

        :type obj: m3_gar_client.data.ObjectBase
        """
        assert isinstance(obj, ObjectBase), type(obj)

        self._obj = obj

    def __iter__(self):
        return iter(self._obj.fields)

    def __getitem__(self, key):
        return getattr(self._obj, key)

    def __len__(self):
        return len(self._obj.fields)

    # pylint: disable=unused-argument
    @property
    def __readonly_exception(self):
        return TypeError("'{}' object is readonly".format(self.__class__.__name__))

    def __setitem__(self, key, value):
        raise self.__readonly_exception

    def __delitem__(self, key):
        raise self.__readonly_exception

    def pop(self, *args):
        raise self.__readonly_exception

    def popitem(self):
        raise self.__readonly_exception

    def clear(self):
        raise self.__readonly_exception

    def update(self, *args, **kwargs):
        raise self.__readonly_exception

    def setdefault(self, key, default=None):
        raise self.__readonly_exception

    # pylint: enable=unused-argument


def _unicode(value):
    return value if isinstance(value, text_type) else text_type(value)


def _unicode_or_empty(value):
    return _unicode(value) if value else ''


def _int(value):
    try:
        return int(value if isinstance(value, int) else int(value))
    except (TypeError, ValueError):
        raise ValueError(value)


def _bool(value):
    try:
        return bool(value if isinstance(value, bool) else bool(value))
    except (TypeError, ValueError):
        raise ValueError(value)


def _int_or_none(value):
    return _int(value) if value else None


def _uuid(value):
    try:
        return text_type(value if isinstance(value, UUID) else UUID(value))
    except (AttributeError, TypeError, ValueError):
        raise ValueError(value)


def _uuid_or_none(value):
    return _uuid(value) if value else None


def _uuid_or_int(value):
    try:
        result = _int(value)
    except ValueError:
        result = _uuid(value)

    return result


def _uuid_or_int_or_none(value):
    return _uuid_or_int(value) if value else None


def _date(value):
    if isinstance(value, date):
        result = value
    else:
        try:
            result = datetime.strptime(value, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            raise ValueError(value)

    return result


def _choices(valid_values, value_type, raw_value):
    value = value_type(raw_value)

    if value not in valid_values:
        raise ValueError(raw_value)

    return value


class AddressObject(ObjectBase):
    """
    Адресный объект.
    """

    #: Поля объекта и признак обязательности значения.
    fields = {
        'id': FieldDescriptor(
            data_type=_int,
            required=True,
            description='Уникальный идентификатор записи (ключевое поле).',
        ),
        'previous_id': FieldDescriptor(
            data_type=_int,
            required=False,
            description='Идентификатор записи связывания с предыдушей исторической записью.',
        ),
        'next_id': FieldDescriptor(
            data_type=_int,
            required=False,
            description='Идентификатор записи  связывания с последующей исторической записью.',
        ),
        'obj_id': FieldDescriptor(
            data_type=_int,
            required=True,
            description='Глобальный уникальный идентификатор адресного объекта.',
        ),
        'guid': FieldDescriptor(
            data_type=_uuid,
            required=True,
            description='UUID адресного объекта.',
        ),
        'level': FieldDescriptor(
            data_type=partial(_choices, GAR_LEVELS, _int),
            required=True,
            description='Уровень адресного объекта.',
        ),
        'ifns_fl_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код ИФНС для физических лиц.',
        ),
        'ifns_fl_territorial_district_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код территориального участка ИФНС ФЛ.',
        ),
        'ifns_ul_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код ИФНС для юридических лиц.',
        ),
        'ifns_ul_territorial_district_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код территориального участка ИФНС ЮЛ.',
        ),
        'okato': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='ОКАТО.',
        ),
        'oktmo': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='ОКТМО.',
        ),
        'kladr_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код адресного объекта одной строкой с признаком актуальности из КЛАДР 4.0.',
        ),
        'kladr_plain_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код адресного объекта из КЛАДР 4.0 одной строкой без признака актуальности (последних двух цифр).',
        ),
        'short_name': FieldDescriptor(
            data_type=_unicode,
            required=True,
            description='Краткое наименование типа объекта',
        ),
        'type_full_name': FieldDescriptor(
            data_type=_unicode,
            required=True,
            description='Полное наименование типа объекта',
        ),
        'official_name': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Официальное наименование',
        ),
        'formal_name': FieldDescriptor(
            data_type=_unicode,
            required=True,
            description='Формализованное наименование',
        ),
        'postal_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Почтовый индекс',
        ),
        'date_of_creation': FieldDescriptor(
            data_type=_date,
            required=True,
            description='Начало действия записи',
        ),
        'date_of_update': FieldDescriptor(
            data_type=_date,
            required=True,
            description='Дата  внесения (обновления) записи',
        ),
        'date_of_expiration': FieldDescriptor(
            data_type=_date,
            required=True,
            description='Окончание действия записи',
        ),
        'full_name': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Полный адрес',
        ),
        'has_children': FieldDescriptor(
            data_type=_bool,
            required=False,
            description='Признак наличия потомков',
        ),
        'region_code': FieldDescriptor(
            data_type=_int,
            required=True,
            description='Код региона',
        ),
        'adm_parent_obj_id': FieldDescriptor(
            data_type=_int,
            required=False,
            description='Родительский obj_id в административной иерархии'
        ),
        'adm_parent_guid': FieldDescriptor(
            data_type=_uuid,
            required=False,
            description='Родительский guid в административной иерархии'
        ),
        'mun_parent_obj_id': FieldDescriptor(
            data_type=_int,
            required=False,
            description='Родительский obj_id в муниципальной иерархии'
        ),
        'mun_parent_guid': FieldDescriptor(
            data_type=_uuid,
            required=False,
            description='Родительский guid в муниципальной иерархии'
        ),
    }


class House(ObjectBase):
    """
    Объект здания (дома).
    """

    fields = {
        'id': FieldDescriptor(
            data_type=_int,
            required=True,
            description='Уникальный идентификатор записи дома',
        ),
        'obj_id': FieldDescriptor(
            data_type=_int,
            required=True,
            description='Глобальный уникальный идентификатор дома',
        ),
        'guid': FieldDescriptor(
            data_type=_uuid,
            required=True,
            description='UUID адресного объекта.',
        ),
        'ifns_fl_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код ИФНС для физических лиц.',
        ),
        'ifns_fl_territorial_district_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код территориального участка ИФНС ФЛ.',
        ),
        'ifns_ul_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код ИФНС для юридических лиц.',
        ),
        'ifns_ul_territorial_district_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Код территориального участка ИФНС ЮЛ.',
        ),
        'okato': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='ОКАТО.',
        ),
        'oktmo': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='ОКТМО.',
        ),
        'postal_code': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Почтовый индекс',
        ),
        'house_number': FieldDescriptor(
            data_type=_unicode,
            required=True,
            description='Номер дома',
        ),
        'building_number': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Номер корпуса',
        ),
        'structure_number': FieldDescriptor(
            data_type=_unicode_or_empty,
            required=False,
            description='Номер строения',
        ),
        'date_of_creation': FieldDescriptor(
            data_type=_date,
            required=True,
            description='Начало действия записи',
        ),
        'date_of_update': FieldDescriptor(
            data_type=_date,
            required=True,
            description='Дата  внесения (обновления) записи',
        ),
        'date_of_end': FieldDescriptor(
            data_type=_date,
            required=True,
            description='Окончание действия записи',
        ),
        'region_code': FieldDescriptor(
            data_type=_int,
            required=True,
            description='Код региона',
        ),
        'adm_parent_obj_id': FieldDescriptor(
            data_type=_int,
            required=False,
            description='Родительский obj_id в административной иерархии'
        ),
        'adm_parent_guid': FieldDescriptor(
            data_type=_uuid,
            required=False,
            description='Родительский guid в административной иерархии'
        ),
        'mun_parent_obj_id': FieldDescriptor(
            data_type=_int,
            required=False,
            description='Родительский obj_id в муниципальной иерархии'
        ),
        'mun_parent_guid': FieldDescriptor(
            data_type=_uuid,
            required=False,
            description='Родительский guid в муниципальной иерархии'
        ),
    }


class ObjectMapper(with_metaclass(ABCMeta, MutableMapping)):
    """
    Обертка над словарями, преобразующая ключи.
    """

    @abstractproperty
    def fields_map(self):
        """Список соответствия ключей.

        :rtype: dict
        """

    def __init__(self, data):  # pylint: disable=super-init-not-called
        assert isinstance(data, dict), type(data)

        self._data = data

    def __len__(self):
        i = 0

        for i, _ in enumerate(iterkeys(self), 1):
            pass

        return i

    def __iter__(self):
        return (field for field in self.fields_map)

    def __getitem__(self, key):
        field_source = self.fields_map[key]

        if callable(field_source):
            # могут быть поля, значение которых не получается вытащить из одного атрибута.
            # для них в fields_map указываем функцию, принимающую весь data единственным аргументом
            value = field_source(self._data)
        else:
            value = self._data.get(field_source)

        return value

    def __setitem__(self, key, value):
        self._data[self.fields_map[key]] = value

    def __delitem__(self, key):
        del self._data[self.fields_map[key]]

    def __bool__(self):
        return bool(self._data)

    __nonzero__ = __bool__
