# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals
import sys

from ..base import ExitCallInterceptor
from appdynamics.lang import str
from appdynamics.lang import import_module
from appdynamics.agent.models.exitcalls import EXIT_CUSTOM, EXIT_SUBTYPE_MONGODB


def load_bson_json_util():
    # Load the pymongo bson module for mongo based deployments.

    # bson.json_util.dumps() is used to convert the bson document to a more readable json format.
    # The json format will then be subject to redaction of any sensitive information in the query.
    mod = None
    try:
        mod = import_module('bson.json_util')
    except ImportError:
        pass
    return mod


def intercept_pymongo(agent, mod):
    class ExitCallListener(mod.monitoring.CommandListener):
        backend_name_format_string = '{HOST}:{PORT} - {DATABASE}'

        def __init__(self):
            self.interceptor = ExitCallInterceptor(agent, None)
            self.exit_call_map = {}
            self.bson_json_util = load_bson_json_util()

        def get_backend(self, connection_id, database_name):
            host, port = connection_id
            backend_properties = {
                'HOST': host,
                'PORT': str(port),
                'DATABASE': database_name,
            }
            backend = self.interceptor.agent.backend_registry.get_backend(EXIT_CUSTOM, EXIT_SUBTYPE_MONGODB,
                                                                          backend_properties,
                                                                          self.backend_name_format_string)
            return backend

        def get_command_str(self, command):
            try:
                return self.bson_json_util.dumps(command)
            except AttributeError:
                return str(command)

        def started(self, event):
            with self.interceptor.log_exceptions():
                bt = self.interceptor.bt
                if bt:
                    backend = self.get_backend(event.connection_id, event.database_name)
                    if backend:
                        exit_call = self.interceptor.start_exit_call(bt, backend, self.get_command_str(event.command))
                        self.exit_call_map[event.operation_id] = exit_call

        def succeeded(self, event):
            self.interceptor.end_exit_call(self.exit_call_map.pop(event.operation_id, None))

        def failed(self, event):
            self.interceptor.end_exit_call(self.exit_call_map.pop(event.operation_id, None), exc_info=sys.exc_info())

    mod.monitoring.register(ExitCallListener())
