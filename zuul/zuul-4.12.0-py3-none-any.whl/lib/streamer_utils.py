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

'''
This file contains code common to finger log streaming functionality.
The log streamer process within each executor, the finger gateway service,
and the web interface will all make use of this module.
'''

import logging
import os
import pwd
import random
import select
import socket
import socketserver
import ssl
import threading
import time

from zuul.exceptions import StreamingError


log = logging.getLogger("zuul.lib.streamer_utils")


class BaseFingerRequestHandler(socketserver.BaseRequestHandler):
    '''
    Base class for common methods for handling finger requests.
    '''

    MAX_REQUEST_LEN = 1024
    REQUEST_TIMEOUT = 10

    def getCommand(self):
        poll = select.poll()
        bitmask = (select.POLLIN | select.POLLERR |
                   select.POLLHUP | select.POLLNVAL)
        poll.register(self.request, bitmask)
        buffer = b''
        ret = None
        start = time.time()
        while True:
            elapsed = time.time() - start
            timeout = max(self.REQUEST_TIMEOUT - elapsed, 0)
            if not timeout:
                raise Exception("Timeout while waiting for input")
            for fd, event in poll.poll(timeout):
                if event & select.POLLIN:
                    x = self.request.recv(self.MAX_REQUEST_LEN)
                    if not x:
                        # This will cause the caller to quietly shut down
                        raise BrokenPipeError
                    buffer += x
                else:
                    raise Exception("Received error event")
            if len(buffer) >= self.MAX_REQUEST_LEN:
                raise Exception("Request too long")
            try:
                ret = buffer.decode('utf-8')
                x = ret.find('\n')
                if x > 0:
                    # rstrip to remove any other unnecessary chars (e.g. \r)
                    return ret[:x].rstrip()
            except UnicodeDecodeError:
                pass


class CustomThreadingTCPServer(socketserver.ThreadingTCPServer):
    '''
    Custom version that allows us to drop privileges after port binding.
    '''

    def __init__(self, *args, **kwargs):
        # NOTE(pabelanger): Set up address_family for socketserver based on the
        # fingergw.listen_address setting in zuul.conf.
        # param tuple args[0]: The address and port to bind to for
        # socketserver.
        server_address = args[0]
        address_family = None
        for res in socket.getaddrinfo(
                server_address[0], server_address[1], 0, self.socket_type):
            if res[0] == socket.AF_INET6:
                # If we get an IPv6 address, break our loop and use that first.
                address_family = res[0]
                break
            elif res[0] == socket.AF_INET:
                address_family = res[0]

        # Check to see if getaddrinfo failed.
        if not address_family:
            raise Exception("getaddrinfo returns an empty list")

        self.address_family = address_family
        self.user = kwargs.pop('user', None)
        self.pid_file = kwargs.pop('pid_file', None)
        self.server_ssl_key = kwargs.pop('server_ssl_key', None)
        self.server_ssl_cert = kwargs.pop('server_ssl_cert', None)
        self.server_ssl_ca = kwargs.pop('server_ssl_ca', None)
        socketserver.ThreadingTCPServer.__init__(self, *args, **kwargs)

    def change_privs(self):
        '''
        Drop our privileges to another user.
        '''
        if os.getuid() != 0:
            return

        pw = pwd.getpwnam(self.user)

        # Change owner on our pid file so it can be removed by us after
        # dropping privileges. May not exist if not a daemon.
        if self.pid_file and os.path.exists(self.pid_file):
            os.chown(self.pid_file, pw.pw_uid, pw.pw_gid)

        os.setgroups([])
        os.setgid(pw.pw_gid)
        os.setuid(pw.pw_uid)
        os.umask(0o022)

    def server_bind(self):
        '''
        Overridden from the base class to allow address reuse and to drop
        privileges after binding to the listening socket.
        '''
        self.allow_reuse_address = True
        socketserver.ThreadingTCPServer.server_bind(self)
        if self.user:
            self.change_privs()

    def server_close(self):
        '''
        Overridden from base class to shutdown the socket immediately.
        '''
        try:
            self.socket.shutdown(socket.SHUT_RD)
            self.socket.close()
        except socket.error as e:
            # If it's already closed, don't error.
            if e.errno == socket.EBADF:
                return
            raise

    def process_request(self, request, client_address):
        '''
        Overridden from the base class to name the thread.
        '''
        t = threading.Thread(target=self.process_request_thread,
                             name='socketserver_Thread',
                             args=(request, client_address))
        t.daemon = self.daemon_threads
        t.start()

    def get_request(self):
        sock, addr = super().get_request()

        if all([self.server_ssl_key, self.server_ssl_cert,
                self.server_ssl_ca]):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.load_cert_chain(self.server_ssl_cert, self.server_ssl_key)
            context.load_verify_locations(self.server_ssl_ca)
            context.verify_mode = ssl.CERT_REQUIRED
            sock = context.wrap_socket(sock, server_side=True)
        return sock, addr


def getJobLogStreamAddress(executor_api, component_registry, uuid,
                           source_zone):
    """
    Looks up the log stream address for the given build UUID.

    Try to find the build request for the given UUID in ZooKeeper
    by searching through all available zones. If a build request
    was found we use the worker information to build the log stream
    address.
    """
    # Search for the build request in ZooKeeper. This iterates over all
    # available zones (inlcuding unzoned) and stops when the UUID is
    # found.
    build_request, worker_zone = executor_api.getByUuid(uuid)

    if build_request is None:
        raise StreamingError("Build not found")

    worker_info = build_request.worker_info
    if not worker_info:
        raise StreamingError("Build did not start yet")

    job_log_stream_address = {}
    if worker_zone and source_zone != worker_zone:
        info = _getFingerGatewayInZone(component_registry, worker_zone)
        if info:
            job_log_stream_address['server'] = info.hostname
            job_log_stream_address['port'] = info.public_port
            job_log_stream_address['use_ssl'] = info.use_ssl
            log.debug('Source (%s) and worker (%s) zone '
                      'are different, routing via %s:%s',
                      source_zone, worker_zone,
                      info.hostname, info.public_port)
        else:
            log.warning('Source (%s) and worker (%s) zone are different'
                        'but no fingergw in target zone found. '
                        'Falling back to direct connection.',
                        source_zone, worker_zone)
    else:
        log.debug('Source (%s) or worker zone (%s) undefined '
                  'or equal, no routing is needed.',
                  source_zone, worker_zone)

    if 'server' not in job_log_stream_address:
        job_log_stream_address['server'] = worker_info["hostname"]
        job_log_stream_address['port'] = worker_info["log_port"]

    return job_log_stream_address


def _getFingerGatewayInZone(component_registry, zone):
    gws = [gw for gw in component_registry.all('fingergw') if gw.zone == zone]
    if gws:
        return random.choice(gws)
    return None
