
import threading
import asyncio
import json
from uuid import uuid4
from datetime import datetime
import logging
from functools import partial

import tornado.ioloop
import tornado.web
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.json_format import MessageToDict

from delphai_backend_utils.config import get_config
from delphai_backend_utils.grpc_calls import _message_template

THIS_UUID = str(uuid4())
STARTED_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class RequestHandler(tornado.web.RequestHandler):

    async def get(self, path):
        method_descriptors = self.settings["method_descriptors"]
        grpc_host_and_port = get_config('server.host_and_port') or '0.0.0.0:8080'
        if not path:
            # Respond a list of functions
            res = {
                'gateway_id': THIS_UUID,
                'started': STARTED_TIME,
                'status': 'active',
                'functions': [{
                    'function_name': meth_name,
                    'branches': [{'name': 'not-defined', 'host': grpc_host_and_port, 'is_default': True}]
                } for meth_name in method_descriptors.keys()]
            }
            self.write(res)
        elif path not in self.settings["method_descriptors"]:
            self._reason = 'Wrong function name'
            self._status_code = 404
            self.finish(f'Wrong function name. Available functions: {", ".join(method_descriptors.keys())}')
            return
        else:
            method_descriptor = self.settings["method_descriptors"][path]
            self.write({
                'function_name': path,
                'branch': 'not-defined',
                'host': grpc_host_and_port,
                'input': _message_template(method_descriptor['input_def']),
                'output': _message_template(method_descriptor['output_def']),
            })
        self.finish()

    async def post(self, path):
        # service_descriptor = self.settings["service_descriptor"]
        if not path:
            self._reason = 'Function name not specified'
            self._status_code = 400
            self.finish('Full function name should be specified in path')
            return
        method_descriptors = self.settings["method_descriptors"]
        if path not in self.settings["method_descriptors"]:
            self._reason = 'Wrong function name'
            self._status_code = 404
            self.finish(f'Wrong function name. Available functions: {", ".join(method_descriptors.keys())}')
            return
        if self.request.body:
            try:
                in_msg_dict = json.loads(self.request.body)
            except Exception as exc:
                self._reason = 'Wrong JSON'
                self._status_code = 400
                self.finish(f'Wrong JSON: {exc}')
                return
        else:
            in_msg_dict = {}
        if not isinstance(in_msg_dict, dict):
            self._reason = 'Wrong JSON'
            self._status_code = 400
            self.finish('Wrong JSON: must be a single object')
            return

        try:
            in_msg = method_descriptors[path]['input_type'](**in_msg_dict)
        except Exception as exc:
            self._reason = 'Wrong message format'
            self._status_code = 400
            self.finish(f'Wrong message format: {exc}')
            return

        try:
            loop = asyncio.get_event_loop()
            func = partial(method_descriptors[path]['method'], in_msg, None)  # TODO: implement context parameter
            res = await loop.run_in_executor(None, func)
        except Exception as exc:
            self._reason = 'Internal Server Error'
            self._status_code = 500
            self.finish(f'Error: {exc}')
            return

        self.write(MessageToDict(res, preserving_proto_field_name=True))
        self.finish()


class WebServer(threading.Thread):
    service_descriptor = None
    grpc_server = None

    def run(self):
        gateway_host_and_port = get_config('server.gateway_host_and_port') or '0.0.0.0:7070'
        split_host_and_port = gateway_host_and_port.split(':')
        if len(split_host_and_port) == 1:
            raise ValueError('Wrong server.gateway_host_and_port value. Expected: <host>:<port>')
        if not split_host_and_port[-1].isnumeric():
            raise ValueError('Wrong server.gateway_host_and_port value. Port must be numeric')

        _sym_db = _symbol_database.Default()
        method_descriptors = {}  # full name -> {method, input_type, output_type}
        for service_handler in self.grpc_server._state.generic_handlers:
            if service_handler._name.startswith('grpc.reflection.'):
                continue
            for meth_key, meth_handler in service_handler._method_handlers.items():
                meth_key = meth_key[1:].replace('/', '.')
                service_name, method_name = meth_key.split('.')[2:]
                meth_descr = self.service_descriptor.services_by_name[service_name].methods_by_name[method_name]
                method_descriptors[meth_key] = {
                    'method': meth_handler.unary_unary,
                    'input_def': meth_descr.input_type,
                    'output_def': meth_descr.output_type,
                    'input_type': _sym_db.GetPrototype(meth_descr.input_type),
                    'output_type': _sym_db.GetPrototype(meth_descr.output_type),
                }

        asyncio.set_event_loop(asyncio.new_event_loop())
        application = tornado.web.Application([
            (r"/(.*)", RequestHandler)],
            default_host=':'.join(split_host_and_port[:-1]),
            service_descriptor=self.service_descriptor,
            method_descriptors=method_descriptors)
        application.listen(int(split_host_and_port[-1]))
        logging.info(f'Started gateway {gateway_host_and_port}')
        tornado.ioloop.IOLoop.instance().start()


def run_own_gateway(service_descriptor, grpc_server):
    server = WebServer(daemon=True)
    server.service_descriptor = service_descriptor
    server.grpc_server = grpc_server
    server.start()
