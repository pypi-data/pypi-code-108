import json
import time
import copy

import requests
from requests.exceptions import ConnectionError

from metasdk.logger import LOGGER_ENTITY
from metasdk.exceptions import RetryHttpRequestError, EndOfTriesError, UnexpectedError, ApiProxyError, RateLimitError, \
    ApiProxyBusinessErrorMixin


class ApiProxyService:

    MAX_PAGES = 100000

    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}
        self.__data_get_cache = {}
        self.__data_get_flatten_cache = {}

    def __api_proxy_call(self, engine, payload, method, analyze_json_error_param, retry_request_substr_variants,
                         stream=False, raise_business_errors=False):
        """
        :param engine: Система
        :param payload: Данные для запроса
        :param method: string Может содержать native_call | tsv | json_newline
        :param analyze_json_error_param: Нужно ли производить анализ параметра error в ответе прокси
        :param retry_request_substr_variants: Список подстрок, при наличии которых в ответе будет происходить перезапрос
        :param stream:
        :return:
        """
        log_ctx = {
            "engine": engine,
            "method": payload.get('method'),
            "method_params": payload.get('method_params')
        }
        self.__app.log.info("Call api proxy", log_ctx)
        body = {
            "engine": engine,
            "payload": payload
        }
        for _try_idx in range(20):
            try:
                # 1h таймаут, так как бывают большие долгие данные, а лимит хоть какой-то нужен
                body_str = json.dumps(body)
                headers = {
                    "User-Agent": self.__app.user_agent,
                    "X-App": "META",
                    "X-Worker": self.__app.service_id,
                    "X-ObjectLocator": LOGGER_ENTITY.get("objectLocator")
                }
                resp = requests.post(self.__app.api_proxy_url + "/" + method, body_str, timeout=3600, stream=stream,
                                     headers=headers)

                self.check_err(resp, analyze_json_error_param=analyze_json_error_param,
                               retry_request_substr_variants=retry_request_substr_variants,
                               raise_business_errors=raise_business_errors)
                return resp
            except (RetryHttpRequestError, RateLimitError, ConnectionError) as e:
                self.__app.log.warning("Sleep retry query: " + str(e), log_ctx)
                sleep_time = 20

                if e.__class__.__name__ == "RateLimitError":
                    sleep_time = e.waiting_time

                time.sleep(sleep_time)
        raise EndOfTriesError("Api of api proxy tries request")

    def call_proxy_with_paging(self, engine, payload, method, analyze_json_error_param, retry_request_substr_variants,
                               max_pages=MAX_PAGES, raise_business_errors=False):
        """
        Постраничный запрос
        :param engine: Система
        :param payload: Данные для запроса
        :param method: string Может содержать native_call | tsv | json_newline
        :param analyze_json_error_param: Нужно ли производить анализ параметра error в ответе прокси
        :param retry_request_substr_variants: Список подстрок, при наличии которых в ответе будет происходить перезапрос
        :param max_pages: Максимальное количество страниц в запросе
        :return: объект генератор
        :param raise_business_errors: Преобразовывать ApiProxyError в конкретную BusinessError
        """
        copy_payload = copy.deepcopy(payload)

        idx = 0
        for idx in range(max_pages):
            resp = self.__api_proxy_call(engine, copy_payload, method, analyze_json_error_param,
                                         retry_request_substr_variants, raise_business_errors=raise_business_errors)
            yield resp

            paging_resp = resp.json().get("paging")
            if not paging_resp:
                break
            copy_payload["paging"] = paging_resp

        if idx >= max_pages:
            self.__app.log.warning("Достигнут максимальный предел страниц", {"max_pages": max_pages})

    def call_proxy(self, engine, payload, method, analyze_json_error_param, retry_request_substr_variants,
                   stream=False, raise_business_errors=False):
        """
        :param engine: Система
        :param payload: Данные для запроса
        :param method: string Может содержать native_call | tsv | json_newline
        :param analyze_json_error_param: Нужно ли производить анализ параметра error в ответе прокси
        :param retry_request_substr_variants: Список подстрок, при наличии которых в ответе будет происходить перезапрос
        :param raise_business_errors: Преобразовывать ApiProxyError в конкретную BusinessError
        :param stream:
        :return:
        """
        return self.__api_proxy_call(engine, payload, method, analyze_json_error_param, retry_request_substr_variants,
                                     stream, raise_business_errors=raise_business_errors)

    @staticmethod
    def check_err(resp, analyze_json_error_param=False, retry_request_substr_variants=None,
                  raise_business_errors=False):
        """
        :type retry_request_substr_variants: list Список вхождений строк, при налиции которых в ошибке апи будет произведен повторный запрос к апи
        """
        if retry_request_substr_variants is None:
            retry_request_substr_variants = []

        # РКН блокировки вызывают ошибку SSL
        retry_request_substr_variants.append("TLSV1_ALERT_ACCESS_DENIED")

        if resp.status_code in [502, 503, 504]:
            raise RetryHttpRequestError(resp.text)

        if resp.status_code >= 400:
            rtext = resp.text
            for v_ in retry_request_substr_variants:
                if v_ in rtext:
                    raise RetryHttpRequestError(rtext)
            raise UnexpectedError("HTTP request failed: {} {}".format(resp.status_code, rtext))
        if analyze_json_error_param:
            data_ = resp.json()
            error = data_.get("error")
            if error:
                full_err_ = json.dumps(error, ensure_ascii=False)

                if error.get("type") == "RateLimitError":
                    raise RateLimitError(error.get("message"), waiting_time=error.get("waiting_time"))

                for v_ in retry_request_substr_variants:
                    if v_ in full_err_:
                        raise RetryHttpRequestError(full_err_)
                if raise_business_errors:
                    for cls in ApiProxyBusinessErrorMixin.__subclasses__():
                        if cls.__name__ == error.get("type"):
                            raise cls(full_err_)
                raise ApiProxyError(full_err_)
        return resp
