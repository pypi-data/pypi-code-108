import logging

from metasdk.logger import LOGGER_ENTITY, REQUEST_LOG


def preprocessing(func):
    def wrapper(self, msg, context=None):
        """ Этот декоратор занимается предобработкой входных параметров:
            1. Проверяет context на None.
            2. Добавляет к msg имя класса объекта ошибки. Например: msg + ModuleNotFoundError
         """
        if context is None:
            context = {}

        error_obj = context.get('e')
        if isinstance(error_obj, Exception):
            try:
                msg = msg + ' ' + str(error_obj.__class__.__name__)
            except Exception:
                pass

        return func(self, msg, context)
    return wrapper


async def error_log_middleware(request, handler):
    try:
        Logger.log_request(method=request.method,
                           url=str(request.url),
                           user_agent=request.headers.get("User-Agent", "-"),
                           referrer=request.headers.get("Referrer", "-"),  # TODO check how it work
                           response_status_code=0,
                           remote_ip=request.remote)
    except Exception as e:
        Logger().info("Can't log request", {"request": str(request), "exception": e})
    response = await handler(request)
    try:
        Logger.set_log_request_response_status_code(response.status)
        if response.status >= 400:
            Logger().error("Http request error")
    except Exception as e:
        Logger().info("Can't log request", {"request": str(request), "exception": e, "response": str(response)})
    return response

# Нужно для работы в aiohttp (см. реализацию декоратор middleware в aiohttp)
error_log_middleware.__middleware_version__ = 1


class Logger:
    """
    Прослойка для упрощения апи логгера
    """

    def set_entity(self, key, value):
        if value is None:
            self.remove_entity(key)
        else:
            LOGGER_ENTITY[key] = value

    @staticmethod
    def log_request(method: str, url: str, user_agent: str, response_status_code: int = 0,
                    referrer: str = "-", remote_ip:str = "-"):
        REQUEST_LOG.update({"method": method,
                            "url": url,
                            "userAgent": user_agent,
                            "responseStatusCode": response_status_code,
                            "referrer": referrer,
                            "remoteIp": remote_ip})

    @staticmethod
    def set_log_request_response_status_code(response_status_code: int):
        REQUEST_LOG["responseStatusCode"] = response_status_code

    @staticmethod
    def remove_entity(key):
        LOGGER_ENTITY.pop(key, None)

    @staticmethod
    def info(msg, context=None):
        if context is None:
            context = {}
        logging.info(msg, extra={'context': context})

    @preprocessing
    def warning(self, msg, context):
        logging.warning(msg, extra={'context': context})

    @preprocessing
    def error(self, msg, context):
        logging.error(msg, extra={'context': context})

    @preprocessing
    def critical(self, msg, context):
        logging.critical(msg, extra={'context': context})

    @preprocessing
    def exception(self, msg, context):
        logging.exception(msg, extra={'context': context})
