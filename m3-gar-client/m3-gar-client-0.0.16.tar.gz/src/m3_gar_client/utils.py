# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from m3_gar_client.constants import GAR_HIERARCHIES
from m3_gar_client.constants import GAR_HIERARCHY_MUN
from m3_gar_client.data import AddressObject
from m3_gar_client.data import House


class cached_property(property):
    """Кешируемое свойство.

    В отличие от :class:`django.utils.functional.cached_property`, наследуется
    от property и копирует строку документации, что актуально при генерации
    документации средствами Sphinx.
    """

    def __init__(self, method):
        super(cached_property, self).__init__(method)

        self.__doc__ = method.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.fget.__name__ not in instance.__dict__:
            instance.__dict__[self.fget.__name__] = self.fget(instance)

        return instance.__dict__[self.fget.__name__]


def correct_keyboard_layout(text):
    """При необходимости меняет раскладку клавиатуры.

    :param unicode text: Текстовая строка, подлежащая корректировке.

    :rtype: unicode
    """
    en_chars = (
        '`~@#$^&'
        'qwertyuiop[]'
        'QWERTYUIOP{}'
        'asdfghjkl;\''
        'ASDFGHJKL:"|'
        'zxcvbnm,./'
        'ZXCVBNM<>?'
    )

    ru_chars = (
        'ёЁ"№;:?'
        'йцукенгшщзхъ'
        'ЙЦУКЕНГШЩЗХЪ'
        'фывапролджэ'
        'ФЫВАПРОЛДЖЭ/'
        'ячсмитьбю.'
        'ЯЧСМИТЬБЮ,'
    )

    assert len(en_chars) == len(ru_chars)

    ru_only_chars = set(ru_chars) - set(en_chars)
    if set(text).isdisjoint(ru_only_chars):
        # Текст не содержит ни одного символа из русской раскладки, значит
        # раскладку надо поменять.

        def translate():
            for char in text:
                position = en_chars.find(char)
                yield char if position == -1 else ru_chars[position]

        result = ''.join(translate())
    else:
        result = text

    # Сделано здесь до того момента, пока не будет сделана обработка на стороне
    # REST API
    result = result.replace('ё', 'е').replace('Ё', 'Е')

    return result


def find_address_objects(filter_string, levels=None, typenames=None, parent_id=None, timeout=None):
    """Возвращает адресные объекты, соответствующие параметрам поиска.

    :param unicode filter_string: Строка поиска.
    :param levels: Уровни адресных объектов, среди которых нужно осуществлять поиск.
    :param parent_id: ID родительского объекта.
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: generator
    """
    from m3_gar_client import config

    return config.backend.find_address_objects(filter_string, levels, typenames, parent_id, timeout)


def get_address_object(obj_id, timeout=None):
    """Возвращает адресный объект ГАР по его ID.

    :param obj_id: ID адресного объекта ГАР.
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: m3_gar_client.data.AddressObject or NoneType
    """
    from m3_gar_client import config

    return config.backend.get_address_object(obj_id, timeout)


def find_house(house_number='', parent_id=None, building_number=None, structure_number=None, timeout=None):
    """Возвращает информацию о здании по его номеру.

    :param unicode house_number: Номер дома.
    :param parent_id: ID родительского объекта.
    :param unicode building_number: Номер корпуса.
    :param unicode structure_number: Номер строения.
    :param parent_id: ID родительского объекта.
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: m3_gar_client.data.House or NoneType
    """
    from m3_gar_client import config

    return config.backend.find_house(house_number, parent_id, building_number, structure_number, timeout)


def get_house(house_id, timeout=None):
    """Возвращает информацию о здании по его ID в ГАР.

    .. important::

       В ГАР здания с разными корпусами/строениями имеют разные ID.
       Например, "д.1 корп. 1" и "д.1 корп. 2" будут иметь разные
       идентификаторы.

    :param house_id: ID здания.
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: m3_gar_client.data.House
    """
    from m3_gar_client import config

    return config.backend.get_house(house_id, timeout)


def get_address_object_name(address_object):
    """Возвращает наименование объекта с кратким наименованием его типа.

    Примеры:

      * Забайкальский край
      * ул. Ленина
      * г. Казань

    :type address_object: m3_gar_client.data.AddressObject

    :rtype: unicode
    """
    if address_object.guid == 'd66e5325-3a25-4d29-ba86-4ca351d9704b':
        # Ханты-Мансийский Автономный округ - Югра
        result = address_object.formal_name
    elif address_object.short_name in ('край', 'АО', 'Аобл', 'обл'):
        result = '{} {}'.format(address_object.formal_name, address_object.short_name)
    else:
        result = '{}. {}'.format(address_object.short_name, address_object.formal_name)

    return result


def get_house_name(house):
    """Возвращает полное наименование здания.

    Примеры:

      * д. 1
      * д. 2 корп. 3
      * корп. 5
      * д. 4 стр. 5
      * стр. 9
      * д. 6 корп. 7 стр. 8

    :type house: m3_gar_client.data.House

    :rtype: unicode
    """
    assert isinstance(house, House), type(house)

    names = []
    if house.house_number:
        names.append('д. ' + house.house_number)
    if house.building_number:
        names.append('корп. ' + house.building_number)
    if house.structure_number:
        names.append('стр. ' + house.structure_number)

    return ', '.join(names)


def get_full_name(obj, hierarchy=GAR_HIERARCHY_MUN, with_postal_code=True, timeout=None):
    """Возвращает полное наименование адресного объекта или здания.

    Примеры:

      * Забайкальский край, г. Чита
      * Новосибирская обл., г. Новосибирск, ул. Вокзальная магистраль, д. 1/1
      * д. 1 корп. 3 стр. 2

    :type obj: m3_gar_client.data.AddressObject or m3_gar_client.data.House
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: unicode
    """
    postal_code = None
    names = []

    if not isinstance(obj, (House, AddressObject)):
        raise TypeError(obj)

    for addrobj in get_full_details(obj, hierarchy=hierarchy):
        if postal_code is None and addrobj.postal_code:
            postal_code = addrobj.postal_code

        if isinstance(addrobj, House):
            names.append(get_house_name(addrobj))

        elif isinstance(addrobj, AddressObject):
            names.append(get_address_object_name(addrobj))

    if with_postal_code and postal_code is not None:
        names.insert(0, postal_code)

    full_name = ', '.join(reversed(names))

    return full_name


def get_full_details(obj, hierarchy=GAR_HIERARCHY_MUN, timeout=None):
    """
    Возвращает полный список объектов, снизу вверх из иерархии.
    """
    if not isinstance(obj, (House, AddressObject)):
        raise TypeError(obj)

    if hierarchy not in GAR_HIERARCHIES:
        raise ValueError(hierarchy)

    parent_attr = f'{hierarchy}_parent_obj_id'

    objects = []

    if isinstance(obj, House):
        objects.append(obj)

        parent_id = getattr(obj, parent_attr)
        if parent_id:
            obj = get_address_object(parent_id, timeout)

    if isinstance(obj, AddressObject):
        while obj:
            objects.append(obj)

            parent_id = getattr(obj, parent_attr)
            if parent_id:
                obj = get_address_object(parent_id, timeout)
            else:
                break

    return objects


def get_details(obj, timeout=None):
    """
    Возвращает список наименований и сокращений узла, снизу вверх из иерархии.
    Не включая верхний уровень "Субъект РФ"
    """
    result = get_full_details(obj, timeout=timeout)

    return result[1:] if len(result) > 1 else result
