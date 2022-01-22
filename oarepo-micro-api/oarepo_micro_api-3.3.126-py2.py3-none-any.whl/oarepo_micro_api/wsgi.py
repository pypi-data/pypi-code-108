# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""WSGI application for OARepo Micro API."""
from invenio_app.factory import create_api
# APPLICATION_ROOT='/api' has to be set for this to work !
from oarepo_heartbeat.views import environ, liveliness, readiness

print('Application loading ...')


class PrefixMiddleware(object):
    """/api prefixing WSGI middleware."""

    def __init__(self, app):
        """Initialize prefixing middleware."""
        self.app = app

    def __call__(self, envir, start_response):
        """Sets /api prefix on the request path."""
        path_info = envir['PATH_INFO']
        script = ''
        if path_info.startswith('/api'):
            script = '/api'
            path_info = path_info[4:]
        original_script_name = envir.get("SCRIPT_NAME", "")
        envir["SCRIPT_NAME"] = original_script_name + script
        envir["PATH_INFO"] = path_info
        return self.app(envir, start_response)


class HeartbeatMiddleware:
    """HeartBeat endpoints WSGI middleware."""

    def __init__(self, app):
        """Initialize heartbeat middleware."""
        self.app = app

    def __call__(self, envir, start_response):
        """Handle .well-known endpoints outside of /api prefix."""
        rsp = None
        with application.app_context():
            pi = envir.get('PATH_INFO', '')
            if pi == '/.well-known/heartbeat/readiness':
                rsp = readiness()
            elif pi == '/.well-known/heartbeat/liveliness':
                rsp = liveliness()
            elif pi == '/.well-known/heartbeat/environ':
                rsp = environ()
            if rsp:
                return rsp(envir, start_response)
            else:
                return self.app(envir, start_response)


application = create_api()
application.wsgi_app = HeartbeatMiddleware(PrefixMiddleware(application.wsgi_app))
