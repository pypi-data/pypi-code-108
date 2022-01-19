import logging

from quart import Quart, request, g, Request, Response, Blueprint
from .middleware_appinsights import ASGIWrapper as AppInsightsWrapper
from .middleware_request_id import ASGIRequest as RequestIdWrapper


class Framework():
    def aml_app(self, name):
        return Quart(name)

    def wrap_request_id(self, app):
        app.asgi_app = RequestIdWrapper(app.asgi_app)

    def wrap_appinsights(self, app, appinsights_client):
        app.asgi_app = AppInsightsWrapper(app.asgi_app, appinsights_client)

    def wrap_debuggability(self, app, logger):
        pass

    def prepare_loggers(self):
        formatter = logging.Formatter(fmt='[%(asctime)s] %(message)s', datefmt='%d/%b/%Y:%H:%M:%S %z')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        # uvicorn access log
        logger = logging.getLogger("uvicorn.access")
        logger.addHandler(handler)
        logger.addFilter(lambda record: 'GET / HTTP/1.' not in record.getMessage())

        # uvicorn error log
        logger = logging.getLogger("uvicorn.error")
        logger.addHandler(handler)
