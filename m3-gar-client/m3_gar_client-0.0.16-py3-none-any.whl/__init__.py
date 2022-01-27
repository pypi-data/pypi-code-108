# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from importlib import import_module
import abc

from django.conf import settings
from six import with_metaclass

from m3_gar_client.utils import cached_property


class Config(with_metaclass(abc.ABCMeta, object)):

    """Базовый класс для конфигурации пакета."""

    @cached_property
    def backend(self):
        """Бэкенд для доступа к данным ГАР.

        :rtype: :class:`m3_gar_client.backends.base.BackendBase`
        """
        backend_class = import_module(settings.GAR['BACKEND']).Backend
        return backend_class()


#: Конфигурация приложения ``m3_gar_client``.
#:
#: Заполняется экземпляром класса :class:`m3_gar_client.Config`, либо его потомком,
#: при инициализации проекта *до* инициализации приложения ``m3-gar-client``.
config = None


if settings.DEBUG:
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
