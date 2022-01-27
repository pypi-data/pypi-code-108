# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

from six import with_metaclass


class BackendBase(with_metaclass(ABCMeta, object)):

    """Базовый класс для бэкендов."""

    @abstractproperty
    def place_search_url(self):
        """URL для поиска населенных пунктов.

        :rtype: str
        """

    @abstractproperty
    def street_search_url(self):
        """URL для поиска улиц.

        :rtype: str
        """

    @abstractproperty
    def house_search_url(self):
        """URL для запроса списка домов.

        :rtype: str
        """

    def configure_place_field(self, field):
        """Настраивает поле "Населенный пункт".

        :param field: Поле "Населенный пункт".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    def configure_street_field(self, field):
        """Настраивает поле "Улица".

        :param field: Поле "Улица".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    def configure_house_field(self, field):
        """Настраивает поле "Дом".

        :param field: Поле "Дом".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    @abstractmethod
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
        :param parent_id: ID родительского объекта.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: generator
        """

    @abstractmethod
    def get_address_object(self, obj_id, timeout=None):
        """Возвращает адресный объект ГАР по его ID.

        :param obj_id: ID адресного объекта ГАР.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: m3_gar_client.data.AddressObject
        """

    @abstractmethod
    def find_house(self, house_number, parent_id, timeout=None):
        """Возвращает информацию о здании по его номеру.

        :param unicode house_number: Номер дома.
        :param parent_id: ID родительского объекта.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: m3_gar_client.data.House or NoneType
        """

    @abstractmethod
    def get_house(self, house_id, timeout=None):
        """Возвращает информацию о здании по его ID в ГАР.

        :param house_id: ID здания.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: m3_gar_client.data.House
        """
