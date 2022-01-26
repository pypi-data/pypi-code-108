import json
import os
import platform
import socket
import sys
import time

import requests
from urllib3.connection import HTTPConnection

from metasdk.__state import set_current_app
from metasdk.event_bus import EventBus
from metasdk.exceptions import UnexpectedError, DbQueryError, ServerError
from metasdk.internal import read_developer_settings
from metasdk.logger import create_logger, eprint
from metasdk.logger.bulk_logger import BulkLogger
from metasdk.logger.logger import Logger
from metasdk.services import get_api_call_headers, process_meta_api_error_code
from metasdk.services.ApiProxyService import ApiProxyService
from metasdk.services.CacheService import CacheService
from metasdk.services.DbQueryService import DbQueryService
from metasdk.services.DbService import DbService
from metasdk.services.DevService import DevService
from metasdk.services.ExportService import ExportService
from metasdk.services.ExternalSystemService import ExternalSystemService
from metasdk.services.FeedService import FeedService
from metasdk.services.IssueService import IssueService
from metasdk.services.MediaService import MediaService
from metasdk.services.MetaqlService import MetaqlService
from metasdk.services.ObjectLogService import ObjectLogService
from metasdk.services.SettingsService import SettingsService
from metasdk.services.UserManagementService import UserManagementService
from metasdk.services.StarterService import StarterService
from metasdk.services.MailService import MailService
from metasdk.services.LockService import LockService
from metasdk.worker import Worker

DEV_STARTER_STUB_URL = "http://STUB_URL"


class MetaApp(object):
    current_app = None  # type: MetaApp
    debug = False
    service_id = None
    build_num = None
    starter_api_url = None
    meta_url = None
    redis_url = None
    api_proxy_url = None
    log = Logger()
    worker = None
    event_bus = None

    # Будет поставляться в конец UserAgent
    user_agent_postfix = ""

    developer_settings = None

    # Пользователь, из под которого пройдет авторизация после того,
    # как мета авторизует разработчика, в случае, если разработчик имеет разрешения для авторизации из-под других пользователей
    auth_user_id = None

    MediaService = None
    MetaqlService = None
    ExportService = None
    CacheService = None
    SettingsService = None
    IssueService = None
    UserManagementService = None
    StarterService = None
    MailService = None
    ApiProxyService = None

    __default_headers = set()
    __db_list = {}

    def __init__(self, service_id: str = None, debug: bool = None,
                 starter_api_url: str = None,
                 meta_url: str = None,
                 api_proxy_url: str = None,
                 include_worker: bool = None,
                 redis_url: str = None,
                 setup_sockets: bool = True
                 ):
        if setup_sockets:
            self.setup_sockets()

        if debug is None:
            is_prod = os.environ.get('PRODUCTION', False)
            debug = os.environ.get('DEBUG', not is_prod)
            if include_worker is None:
                include_worker = True
            if debug == 'false':
                debug = False
        self.debug = debug

        self.redis_url = os.environ.get("REDIS_URL", redis_url or "s1.meta.vmc.loc:6379:1")
        self.meta_url = os.environ.get("META_URL", meta_url or "http://apimeta.devision.io")
        self.api_proxy_url = os.environ.get("API_PROXY_URL", api_proxy_url or "https://apiproxy.apis.garpun.com")

        if debug and not starter_api_url:
            starter_api_url = DEV_STARTER_STUB_URL
        self.starter_api_url = os.environ.get("STARTER_URL", starter_api_url or "http://s2.meta.vmc.loc:28341")

        if service_id:
            self.log.warning("Параметр service_id скоро будет удален из MetaApp")

        gcloud_log_host_port = os.environ.get("GCLOUD_LOG_HOST_PORT", "n3.adp.vmc.loc:31891")
        service_ns = os.environ.get('SERVICE_NAMESPACE', "appscript")  # для ns в логах и для префикса Dispatcher
        service_id = os.environ.get('SERVICE_ID', "local_debug_serivce")
        self.build_num = os.environ.get('BUILD_NUM', '0')
        self.service_ns = service_ns
        self.service_id = service_id
        self.dispatcher_name = self.service_ns + "." + self.service_id

        create_logger(service_id=service_id, service_ns=service_ns, build_num=self.build_num,
                      gcloud_log_host_port=gcloud_log_host_port, debug=self.debug)

        self.__read_developer_settings()

        self.__default_headers = get_api_call_headers(self)
        self.MediaService = MediaService(self)
        self.MetaqlService = MetaqlService(self)
        self.SettingsService = SettingsService(self)
        self.ExportService = ExportService(self)
        self.CacheService = CacheService(self)
        self.IssueService = IssueService(self)
        self.StarterService = StarterService(self, self.db("meta"), self.starter_api_url)
        self.MailService = MailService(self)
        self.DbService = DbService(self)
        self.UserManagementService = UserManagementService(self)
        self.ApiProxyService = ApiProxyService(self)
        self.ExternalSystemService = ExternalSystemService(self)
        self.FeedService = FeedService(self)
        self.LockService = LockService(self)
        self.ObjectLogService = ObjectLogService(self)
        self.DevService = DevService(self)

        if include_worker:
            self.event_bus = EventBus(self)

            stdin = "[]" if debug else ''.join(sys.stdin.readlines())
            self.worker = Worker(self, stdin)

        set_current_app(self)

    def bulk_log(self, log_message=u"Еще одна пачка обработана", total=None, part_log_time_minutes=5):
        """
        Возвращает инстант логгера для обработки списокв данных
        :param log_message: То, что будет написано, когда время придет
        :param total: Общее кол-во объектов, если вы знаете его
        :param part_log_time_minutes: Раз в какое кол-во минут пытаться писать лог
        :return: BulkLogger
        """
        return BulkLogger(log=self.log, log_message=log_message, total=total,
                          part_log_time_minutes=part_log_time_minutes)

    def db(self, db_alias, shard_key=None):
        """
        Получить экземпляр работы с БД
        :type db_alias: basestring Альяс БД из меты
        :type shard_key: Любой тип. Некоторый идентификатор, который поможет мете найти нужную шарду. Тип зависи от принимающей стороны
        :rtype: DbQueryService
        """
        if shard_key is None:
            shard_key = ''

        db_key = db_alias + '__' + str(shard_key)
        if db_key not in self.__db_list:
            self.__db_list[db_key] = DbQueryService(self, {"db_alias": db_alias, "dbAlias": db_alias,
                                                           "shard_find_key": shard_key, "shardKey": shard_key})
        return self.__db_list[db_key]

    @property
    def user_agent(self):
        return self.service_id + " | b" + self.build_num + (
            ' | ' + self.user_agent_postfix if self.user_agent_postfix else "")

    def __read_developer_settings(self):
        """
        Читает конфигурации разработчика с локальной машины или из переменных окружения
        При этом переменная окружения приоритетнее
        :return:
        """
        self.developer_settings = read_developer_settings()
        if not self.developer_settings:
            self.log.warning(
                "НЕ УСТАНОВЛЕНЫ настройки разработчика, это может приводить к проблемам в дальнейшей работе!")

    def api_call(self, service, method, data, options):
        """
        :type app: metasdk.MetaApp
        """
        if 'self' in data:
            # может не быть, если вызывается напрямую из кода,
            # а не из прослоек типа DbQueryService
            data.pop("self")

        if options:
            data.update(options)

        _headers = dict(self.__default_headers)

        if self.auth_user_id:
            _headers['X-META-AuthUserID'] = str(self.auth_user_id)

        request = {
            "url": self.meta_url + "/api/v1/adptools/" + service + "/" + method,
            "data": json.dumps(data),
            "headers": _headers,
            "timeout": (60, 1800)
        }

        last_e = ServerError(request)
        for _try_idx in range(20):
            try:
                resp = requests.post(**request)
                if resp.status_code == 200:
                    decoded_resp = json.loads(resp.text)
                    if 'data' in decoded_resp:
                        return decoded_resp['data'][method]
                    if 'error' in decoded_resp:
                        if 'details' in decoded_resp['error']:
                            eprint(decoded_resp['error']['details'])
                        raise DbQueryError(decoded_resp['error'])
                    raise UnexpectedError()
                else:
                    process_meta_api_error_code(resp.status_code, request, resp.text)
            except (requests.exceptions.ConnectionError, ConnectionError, TimeoutError) as e:
                self.log.warning('META API Connection Error. Sleep...', {"e": e})
                time.sleep(15)

            except ServerError as e:
                last_e = e
                self.log.warning('META Server Error. Sleep...', {"e": e})
                time.sleep(15)

            except Exception as e:
                if 'Служба частично или полностью недоступна' in str(e):
                    self.log.warning('META API Connection Error. Sleep...', {"e": e})
                    time.sleep(15)
                else:
                    raise e

        raise last_e

    def native_api_call(self, service, method, data, options, multipart_form=False, multipart_form_data=None,
                        stream=False, http_path="/api/meta/v1/", http_method='POST',
                        get_params=None, connect_timeout_sec=60, request_timeout_sec=1800):
        """
        :type app: metasdk.MetaApp
        :rtype: requests.Response
        """
        if get_params is None:
            get_params = {}
        if 'self' in data:
            # может не быть, если вызывается напрямую из кода,
            # а не из прослоек типа DbQueryService
            data.pop("self")

        if options:
            data.update(options)

        _headers = dict(self.__default_headers)

        if self.auth_user_id:
            _headers['X-META-AuthUserID'] = str(self.auth_user_id)

        request = {
            "url": self.meta_url + http_path + service + "/" + method,
            "timeout": (connect_timeout_sec, request_timeout_sec),
            "stream": stream,
            "params": get_params,
        }

        if multipart_form:
            if multipart_form_data:
                request['files'] = multipart_form_data
            request['data'] = data
            _headers.pop('content-type', None)
        else:
            request['data'] = json.dumps(data)
        request['headers'] = _headers

        last_e = ServerError(request)
        for _try_idx in range(10):
            try:
                resp = requests.request(http_method, **request)
                # добавляем глобальную трассировку в логи
                self.log.set_entity("request_id", resp.headers.get('request_id'))
                if resp.status_code == 200:
                    return resp
                else:
                    process_meta_api_error_code(resp.status_code, request, resp.text)
            except (requests.exceptions.ConnectionError, ConnectionError, TimeoutError) as e:
                self.log.warning('META API Connection Error. Sleep...', {"e": e})
                time.sleep(15)

            except ServerError as e:
                last_e = e
                self.log.warning('META Server Error. Sleep...', {"e": e})
                time.sleep(15)

            except Exception as e:
                if 'Служба частично или полностью недоступна' in str(e):
                    self.log.warning('META API Service Temporarily Unavailable. Sleep...', {"e": e})
                    time.sleep(15)
                else:
                    raise e
            finally:
                self.log.set_entity("request_id", None)

        raise last_e

    def get_lib_version(self):
        from metasdk import info
        return info.__version__

    @staticmethod
    def setup_sockets():
        """
        Настройка для решения проблемы с разрывом соединения после, примерно, трёх минут при запросе к сервисам,
        расположенным ва яндекс-облаке
        (больше информации в задаче META-2932)
        """

        # Не все из этих параметров есть в каждой системе (в MacOS, например, нет socket.TCP_KEEPIDLE).
        # Если сделать обычные списки, то при интерпретации отсутствующего параметра возникнет исключение.
        # Чтобы этого избежать всё завёрнуто в лямбды
        additional_socket_options_for_systems = {
            "Windows": lambda: [(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                                (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10),
                                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 60),
                                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)],
            "Linux": lambda: [(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                              (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1),
                              (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3),
                              (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)],
            "Darwin": lambda: [(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                               (socket.IPPROTO_TCP, 0x10, 3)]
        }

        HTTPConnection.default_socket_options += additional_socket_options_for_systems[platform.system()]()
