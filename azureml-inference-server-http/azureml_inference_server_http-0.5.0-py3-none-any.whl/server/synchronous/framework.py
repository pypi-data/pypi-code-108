import logging

from flask import Flask, request, g, Request, Response, Blueprint
from .middleware_appinsights import WSGIWrapper as AppInsightsWrapper
from .middleware_request_id import WSGIRequest as RequestIdWrapper
from .middleware_debuggability import init_debuggability


class Framework():
    def aml_app(self, name):
        return Flask(name)

    def wrap_request_id(self, app):
        app.wsgi_app = RequestIdWrapper(app.wsgi_app)

    def wrap_appinsights(self, app, appinsights_client):
        app.wsgi_app = AppInsightsWrapper(app.wsgi_app, appinsights_client)

    def wrap_debuggability(self, app, logger):
        init_debuggability(logger, app)

    def prepare_loggers(self):
        # We're choosing to ignore health endpoint access logs
        logging.getLogger('gunicorn.access').addFilter(lambda record: 'GET / HTTP/1.' not in record.getMessage())
