# coding: utf-8
"""Бэкенд, проксирующий запросы через веб-приложение."""
from __future__ import absolute_import
from __future__ import unicode_literals

from uuid import UUID

from six import text_type

from m3_gar_client.backends.base import BackendBase
from m3_gar_client.backends.m3_rest_gar.proxy.utils import find_address_objects
from m3_gar_client.backends.m3_rest_gar.proxy.utils import find_house
from m3_gar_client.backends.m3_rest_gar.proxy.utils import get_address_object
from m3_gar_client.backends.m3_rest_gar.proxy.utils import get_house


class Backend(BackendBase):
    """
    Бэкенд для работы с сервером m3-rest-gar.
    """

    def __init__(self, *args, **kwargs):
        super(Backend, self).__init__(*args, **kwargs)

        self._pack = None

    @staticmethod
    def _register_parsers():
        """Регистрация парсеров для параметров контекста."""
        from m3.actions.context import DeclarativeActionContext

        params = (
            (
                'm3-gar:unicode-or-none',
                lambda s: text_type(s) if s else None
            ),
            (
                'm3-gar:int-list',
                lambda s: [int(x) for x in s.split(',')]
            ),
            (
                'm3-gar:guid-or-none',
                lambda x: UUID(x) if x else None
            ),
        )

        for name, parser in params:
            DeclarativeActionContext.register_parser(name, parser)

    def register_packs(self):
        """Регистрирует наборы действий в M3."""
        from m3_gar_client import config
        from m3_gar_client.backends.m3_rest_gar.proxy.actions import Pack

        self._register_parsers()

        self._pack = Pack()

        config.controller.extend_packs((
            self._pack,
        ))

    def place_search_url(self):
        """URL для поиска населенных пунктов.

        :rtype: str
        """
        return self._pack.place_search_action.get_absolute_url()

    def street_search_url(self):
        """URL для поиска улиц.

        :rtype: str
        """
        return self._pack.street_search_action.get_absolute_url()

    def house_search_url(self):
        """URL для запроса списка домов.

        :rtype: str
        """
        return self._pack.house_search_action.get_absolute_url()

    def find_address_objects(
        self,
        filter_string,
        levels=None,
        typenames=None,
        parent_id=None,
        timeout=None,
    ):
        """Возвращает адресные объекты, соответствующие параметрам поиска.

        :param unicode filter_string: Строка поиска.
        :param levels: Уровни адресных объектов, среди которых нужно осуществлять поиск.
        :param typenames: Наименования типов адресных объектов, среди которых нужно осуществлять поиск.
        :param parent_id: ID родительского объекта.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: generator
        """
        return find_address_objects(filter_string, levels, typenames, parent_id, timeout)

    def get_address_object(self, obj_id, timeout=None):
        """Возвращает адресный объект ГАР по его ID.

        :param obj_id: ID адресного объекта ГАР.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: m3_gar_client.data.AddressObject
        """
        return get_address_object(obj_id, timeout)

    def find_house(self, house_number, parent_id, building_number, structure_number, timeout=None):
        """Возвращает информацию о здании по его номеру.

        :param unicode house_number: Номер дома.
        :param parent_id: ID родительского объекта.
        :param unicode building_number: Номер корпуса.
        :param unicode structure_number: Номер строения.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: m3_gar_client.data.House or NoneType
        """
        return find_house(house_number, parent_id, building_number, structure_number, timeout)

    def get_house(self, house_id, timeout=None):  # pylint: disable=signature-differs
        """Возвращает информацию о здании по его ID в ГАР.

        :param house_id: ID здания.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: m3_gar_client.data.House
        """
        return get_house(house_id, timeout)
