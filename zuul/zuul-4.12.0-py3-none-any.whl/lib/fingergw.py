# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools
import logging
import socket
import ssl
import threading
from configparser import ConfigParser
from typing import Optional

from zuul.exceptions import StreamingError
from zuul.lib import streamer_utils
from zuul.lib.commandsocket import CommandSocket
from zuul.lib.config import get_default
from zuul.lib.monitoring import MonitoringServer
from zuul.version import get_version_string
from zuul.zk import ZooKeeperClient
from zuul.zk.components import ComponentRegistry, FingerGatewayComponent
from zuul.zk.executor import ExecutorApi

COMMANDS = ['stop']


class RequestHandler(streamer_utils.BaseFingerRequestHandler):
    '''
    Class implementing the logic for handling a single finger request.
    '''

    log = logging.getLogger("zuul.fingergw")

    def __init__(self, *args, **kwargs):
        self.fingergw = kwargs.pop('fingergw')
        super(RequestHandler, self).__init__(*args, **kwargs)

    def _fingerClient(self, server, port, build_uuid, use_ssl):
        '''
        Open a finger connection and return all streaming results.

        :param server: The remote server.
        :param port: The remote port.
        :param build_uuid: The build UUID to stream.

        Both IPv4 and IPv6 are supported.
        '''
        with socket.create_connection((server, port), timeout=10) as s:
            if use_ssl:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                context.verify_mode = ssl.CERT_REQUIRED
                context.check_hostname = self.fingergw.tls_verify_hostnames
                context.load_cert_chain(self.fingergw.tls_cert,
                                        self.fingergw.tls_key)
                context.load_verify_locations(self.fingergw.tls_ca)
                s = context.wrap_socket(s, server_hostname=server)

            # timeout only on the connection, let recv() wait forever
            s.settimeout(None)
            msg = "%s\n" % build_uuid    # Must have a trailing newline!
            s.sendall(msg.encode('utf-8'))
            while True:
                data = s.recv(1024)
                if data:
                    self.request.sendall(data)
                else:
                    break

    def handle(self):
        '''
        This method is called by the socketserver framework to handle an
        incoming request.
        '''
        server = None
        port = None
        try:
            build_uuid = self.getCommand()
            port_location = streamer_utils.getJobLogStreamAddress(
                self.fingergw.executor_api, self.fingergw.component_registry,
                build_uuid, source_zone=self.fingergw.zone)

            if not port_location:
                msg = 'Invalid build UUID %s' % build_uuid
                self.request.sendall(msg.encode('utf-8'))
                return

            server = port_location['server']
            port = port_location['port']
            use_ssl = port_location.get('use_ssl', False)
            self._fingerClient(server, port, build_uuid, use_ssl)
        except StreamingError as e:
            self.request.sendall(str(e).encode("utf-8"))
        except BrokenPipeError:   # Client disconnect
            return
        except Exception:
            self.log.exception(
                'Finger request handling exception (%s:%s):',
                server, port)
            msg = 'Internal streaming error'
            self.request.sendall(msg.encode('utf-8'))
            return


class FingerGateway(object):
    '''
    Class implementing the finger multiplexing/gateway logic.

    For each incoming finger request, a new thread is started that will
    be responsible for finding which Zuul executor is executing the
    requested build (by asking ZooKeeper), forwarding the request to that
    executor, and streaming the results back to our client.
    '''

    log = logging.getLogger("zuul.fingergw")
    handler_class = RequestHandler

    def __init__(
        self,
        config: ConfigParser,
        command_socket: Optional[str],
        pid_file: Optional[str],
    ):
        '''
        Initialize the finger gateway.

        :param config: The parsed Zuul configuration.
        :param str command_socket: Path to the daemon command socket.
        :param str pid_file: Path to the daemon PID file.
        '''

        host = get_default(config, 'fingergw', 'listen_address', '::')
        self.port = int(get_default(config, 'fingergw', 'port', 79))
        self.public_port = int(get_default(
            config, 'fingergw', 'public_port', self.port))
        user = get_default(config, 'fingergw', 'user', None)

        self.address = (host, self.port)
        self.user = user
        self.pid_file = pid_file

        self.server = None
        self.server_thread = None

        self.command_thread = None
        self.command_running = False
        self.command_socket_path = command_socket
        self.command_socket = None

        self.tls_key = get_default(config, 'fingergw', 'tls_key')
        self.tls_cert = get_default(config, 'fingergw', 'tls_cert')
        self.tls_ca = get_default(config, 'fingergw', 'tls_ca')
        self.tls_verify_hostnames = get_default(
            config, 'fingergw', 'tls_verify_hostnames', default=True)
        client_only = get_default(config, 'fingergw', 'tls_client_only',
                                  default=False)
        if (all([self.tls_key, self.tls_cert, self.tls_ca])
            and not client_only):
            self.tls_listen = True
        else:
            self.tls_listen = False

        self.command_map = dict(
            stop=self.stop,
        )

        self.hostname = get_default(config, 'fingergw', 'hostname',
                                    socket.getfqdn())
        self.zone = get_default(config, 'fingergw', 'zone')

        self.zk_client = ZooKeeperClient.fromConfig(config)
        self.zk_client.connect()
        self.component_info = FingerGatewayComponent(
            self.zk_client, self.hostname, version=get_version_string()
        )
        if self.zone is not None:
            self.component_info.zone = self.zone
            self.component_info.public_port = self.public_port
        if self.tls_listen:
            self.component_info.use_ssl = True
        self.component_info.register()

        self.monitoring_server = MonitoringServer(config, 'fingergw',
                                                  self.component_info)
        self.monitoring_server.start()

        self.component_registry = ComponentRegistry(self.zk_client)

        self.executor_api = ExecutorApi(self.zk_client, use_cache=False)

    def _runCommand(self):
        while self.command_running:
            try:
                command = self.command_socket.get().decode('utf8')
                if command != '_stop':
                    self.command_map[command]()
                else:
                    return
            except Exception:
                self.log.exception("Exception while processing command")

    def _run(self):
        try:
            self.server.serve_forever()
        except Exception:
            self.log.exception('Abnormal termination:')
            raise

    def start(self):
        kwargs = dict(
            user=self.user,
            pid_file=self.pid_file,
        )
        if self.tls_listen:
            kwargs.update(dict(
                server_ssl_ca=self.tls_ca,
                server_ssl_cert=self.tls_cert,
                server_ssl_key=self.tls_key,
            ))

        self.server = streamer_utils.CustomThreadingTCPServer(
            self.address,
            functools.partial(self.handler_class, fingergw=self),
            **kwargs)

        # Update port that we really use if we configured a port of 0
        if self.public_port == 0:
            self.public_port = self.server.socket.getsockname()[1]
            self.component_info.public_port = self.public_port

        # Start the command processor after the server and privilege drop
        if self.command_socket_path:
            self.log.debug("Starting command processor")
            self.command_socket = CommandSocket(self.command_socket_path)
            self.command_socket.start()
            self.command_running = True
            self.command_thread = threading.Thread(
                target=self._runCommand, name='command')
            self.command_thread.daemon = True
            self.command_thread.start()

        # The socketserver shutdown() call will hang unless the call
        # to server_forever() happens in another thread. So let's do that.
        self.server_thread = threading.Thread(target=self._run)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.component_info.state = self.component_info.RUNNING

        self.log.info("Finger gateway is started")

    def stop(self):
        self.component_info.state = self.component_info.STOPPED

        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
                self.server = None
            except Exception:
                self.log.exception("Error stopping TCP server:")

        if self.command_socket:
            self.command_running = False

            try:
                self.command_socket.stop()
            except Exception:
                self.log.exception("Error stopping command socket:")

        self.zk_client.disconnect()
        self.monitoring_server.stop()

        self.log.info("Finger gateway is stopped")

    def wait(self):
        '''
        Wait on the gateway to shutdown.
        '''
        self.server_thread.join()

        if self.command_thread:
            self.command_thread.join()
        self.monitoring_server.join()
