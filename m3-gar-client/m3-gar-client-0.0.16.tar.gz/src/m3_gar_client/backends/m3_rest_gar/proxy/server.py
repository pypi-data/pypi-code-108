# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod
import hashlib
import json

from django.utils.functional import SimpleLazyObject
from requests import Session
from six import with_metaclass
from six.moves import http_client

from m3_gar_client.utils import cached_property


class ServerBase(with_metaclass(ABCMeta, object)):
    """
    Базовый класс для серверов ГАР.
    """

    def __init__(self, **kwargs):
        self._base_url = kwargs['url']
        self._timeout = kwargs.get('timeout')

    @property
    def base_url(self):
        return self._base_url

    @property
    @abstractmethod
    def _session(self):
        """HTTP-сессия с сервером m3-rest-gar.

        :rtype: requests.sessions.Session
        """

    def get(self, path, params=None, timeout=None):
        """Возвращает ответ на HTTP-запрос к API сервера ГАР.

        :rtype: requests.models.Response
        """
        response = self._session.get(
            self.base_url.rstrip('/') + path,
            params=params or {},
            timeout=timeout or self._timeout,
        )
        return response


class CachingMixin(object):
    """Класс-примесь для кэширования ответов на запросы.

    Параметры:

        * ``cache`` --- объект кэша. Рекомендуется использовать
          ```django.core.cache.cache`.
        * ``cache_key_prefix`` --- префикс для ключей в кэше.
        * ``cache_timeout`` --- длительность кэширования (в секундах).
    """

    def __init__(self, **kwargs):
        super(CachingMixin, self).__init__(**kwargs)

        self._cache = kwargs['cache']
        self._cache_key_prefix = kwargs.get('cache_key_prefix', 'm3-gar')
        self._cache_timeout = kwargs.get('cache_timeout', 24 * 60 * 60)

    def get(self, path, params=None, timeout=None):
        hasher = hashlib.sha1()
        hasher.update(':'.join((
            self._cache_key_prefix,
            path,
            json.dumps(params, sort_keys=True),
        )).encode('utf-8'))
        cache_key = hasher.hexdigest()

        if cache_key in self._cache:
            response = self._cache.get(cache_key)
        else:
            response = super(CachingMixin, self).get(path, params, timeout)

            if response.status_code == http_client.OK:
                self._cache.set(cache_key, response,)

        return response


class SimpleServer(ServerBase):
    """Сервер ГАР без аутентификации.

    Параметры:

        * ``url`` --- URL API сервера ГАР.
        * ``timeout`` --- timeout запроса к серверу ГАР в секундах.
    """

    @cached_property
    def _session(self):
        result = Session()

        result.trust_env = True

        return result


class SimpleCachingServer(CachingMixin, SimpleServer):
    """
    Сервер ГАР с кешированием без аутентификации.

    Параметры:

        * ``url`` --- URL API сервера ГАР.
        * ``timeout`` --- timeout запроса к серверу ГАР в секундах.
        * ``cache`` --- объект кэша. Рекомендуется использовать
          ```django.core.cache.cache`.
        * ``cache_key_prefix`` --- префикс для ключей в кэше.
        * ``cache_timeout`` --- длительность кэширования (в секундах).
    """


class OAuth2Server(ServerBase):  # pragma: no cover
    """Сервер ГАР с аутентификацией OAuth2.

    Параметры:

        * ``url`` --- URL API сервера ГАР.
        * ``timeout`` --- timeout запроса к серверу ГАР в секундах.
        * ``token_url`` --- Token endpoint URL, must use HTTPS.
        * ``client_id``.
        * ``username`` --- Username used by LegacyApplicationClients..
        * ``password`` --- Password used by LegacyApplicationClients..
        * ``client_secret``.

    .. seealso::

       :meth:`requests_oauthlib.OAuth2Session.fetch_token`
    """

    def __init__(self, **kwargs):
        super(OAuth2Server, self).__init__(**kwargs)

        self.token_url = kwargs['token_url']
        self.client_id = kwargs['client_id']
        self.client_secret = kwargs['client_secret']
        self.username = kwargs['username']
        self.password = kwargs['password']

    @cached_property
    def _session(self):
        from oauthlib.oauth2 import LegacyApplicationClient
        from requests_oauthlib import OAuth2Session

        result = OAuth2Session(
            client=LegacyApplicationClient(self.client_id)
        )
        result.trust_env = True
        result.fetch_token(
            token_url=self.token_url,
            username=self.username,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        return result


class OAuth2CachingServer(CachingMixin, OAuth2Server):
    """Сервер ГАР с кешированием и аутентификацией OAuth2.

    Параметры:

        * ``url`` --- URL API сервера ГАР.
        * ``timeout`` --- timeout запроса к серверу ГАР в секундах.
        * ``token_url`` --- Token endpoint URL, must use HTTPS.
        * ``client_id``.
        * ``username`` --- Username used by LegacyApplicationClients..
        * ``password`` --- Password used by LegacyApplicationClients..
        * ``client_secret``.
        * ``cache`` --- объект кэша. Рекомендуется использовать
          ```django.core.cache.cache`.
        * ``cache_key_prefix`` --- префикс для ключей в кэше.
        * ``cache_timeout`` --- длительность кэширования (в секундах).

    .. seealso::

       :meth:`requests_oauthlib.OAuth2Session.fetch_token`
    """


def get_server():
    """Возвращает сервер ГАР, созданный в соответствии с настройками m3-gar-client.

    Параметры подключения к серверу m3-rest-gar должны быть размещены в
    настройках Django (``django.conf.settings``) в параметре ``GAR``, который
    должен содержать словарь со следующими ключами:

        - ``URL`` --- URL API сервера ГАР.
        - ``TIMEOUT`` --- timeout запроса к серверу ГАР в секундах.
        - ``USE_CACHE`` --- определяет необходимость кеширования HTTP-запросов
          к серверу m3-rest-gar. Значение по умолчанию: ``False``
        - ``USE_SIMPLE_SERVER`` --- Использовать простой сервер, по умолчанию будет использоваться сервер OAUTH2
        - ``OAUTH2`` --- параметры OAuth2: необходиы если не указано использовать простой сервер

          - ``TOKEN_URL`` --- Token endpoint URL, must use HTTPS.
          - ``CLIENT_ID``
          - ``CLIENT_SECRET``
          - ``USERNAME``
          - ``PASSWORD``

    :rtype: m3_gar_client.backends.m3_rest_gar.ServerBase
    """
    from django.conf import settings

    if settings.GAR.get('USE_CACHE', False):
        from django.core.cache import cache

        if settings.GAR.get('USE_SIMPLE_SERVER', False):
            result = SimpleCachingServer(
                url=settings.GAR['URL'],
                timeout=settings.GAR.get('TIMEOUT'),
                cache=cache,
            )

        else:
            result = OAuth2CachingServer(
                url=settings.GAR['URL'],
                timeout=settings.GAR.get('TIMEOUT'),
                cache=cache,
                token_url=settings.GAR['OAUTH2']['TOKEN_URL'],
                client_id=settings.GAR['OAUTH2']['CLIENT_ID'],
                client_secret=settings.GAR['OAUTH2'].get('CLIENT_SECRET'),
                username=settings.GAR['OAUTH2'].get('USERNAME'),
                password=settings.GAR['OAUTH2'].get('PASSWORD'),
            )

    else:
        if settings.GAR.get('USE_SIMPLE_SERVER', False):
            result = SimpleServer(
                url=settings.GAR['URL'],
                timeout=settings.GAR.get('TIMEOUT'),
            )

        else:
            result = OAuth2Server(
                url=settings.GAR['URL'],
                timeout=settings.GAR.get('TIMEOUT'),
                token_url=settings.GAR['OAUTH2']['TOKEN_URL'],
                client_id=settings.GAR['OAUTH2']['CLIENT_ID'],
                client_secret=settings.GAR['OAUTH2'].get('CLIENT_SECRET'),
                username=settings.GAR['OAUTH2'].get('USERNAME'),
                password=settings.GAR['OAUTH2'].get('PASSWORD'),
            )

    return result


server = SimpleLazyObject(get_server)
