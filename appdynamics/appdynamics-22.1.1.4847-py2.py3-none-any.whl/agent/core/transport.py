# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Transports for talking to the Java proxy via ZMQ.

"""

from __future__ import unicode_literals
import time
import os

import appdynamics_bindeps.zmq as zmq
import appdynamics_bindeps.zmq.auth as auth

from appdynamics import config
from appdynamics.lib import set_fields, validate_file_permissions
from appdynamics.agent.core.logs import setup_logger
from appdynamics.agent.core.pb import (
    ASyncRequest,
    ASyncMessage,
    StartNodeRequest,
    ConfigResponse,
    BTInfoResponse,
    StartNodeResponse,
    serialize_message,
    parse_message,
    pb_from_dict,)

__all__ = [
    'BaseTransport',
    'ControlTransport',
    'ConfigTransport',
    'InfoTransport',
    'ReportingTransport'
]


class BaseStrategy(object):
    def before_connect(self, socket, timeout_ms):
        pass

    def after_connect(self, socket, timeout_ms):
        return True


class SleepConnectionStrategy(BaseStrategy):
    """A fallback connection-detection strategy that sleeps.

    This isn't a good choice for production use because it's both
    unreliable (there's no guarantee we sleep long enough for the
    connection to complete) and slow (it's likely we sleep longer
    than what it takes to connect).

    """
    def after_connect(self, socket, timeout_ms):
        time.sleep(timeout_ms / 1000.0)
        return True


class PollBindConnectionStrategy(BaseStrategy):
    """A connection-detection strategy using the AppD patched ZeroMQ.

    """
    def after_connect(self, socket, timeout_ms):
        return bool(socket.poll(timeout_ms, zmq.POLLBIND))


class PollOutConnectionStrategy(BaseStrategy):
    """A connection-detection strategy for REQ type sockets.

    """
    def after_connect(self, socket, timeout_ms):
        return bool(socket.poll(timeout_ms, zmq.POLLOUT))


def decide_connection_strategy():
    if hasattr(zmq, 'POLLBIND'):
        return PollBindConnectionStrategy()
    else:
        return SleepConnectionStrategy()


DEFAULT_STRATEGY = decide_connection_strategy()


class BaseTransport(object):
    """Base class for ZeroMQ transports.
    Note: For TCP, addr and socket_name will be used for host and port respectively
    """
    SOCKET_TYPE = zmq.ROUTER

    def __init__(self):
        super(BaseTransport, self).__init__()
        self.logger = setup_logger('appdynamics.agent')
        self.socket = None
        self.addr = None

    def connect(self, addr, timeout_ms=100, strategy=None, **kwargs):
        """Connect the underlying ZMQ socket, blocking until the connection completes.

        :param bytes addr: the ZeroMQ address to connect to
        :param int timeout_ms: the connection timeout (in ms)
        :return: true if we detected that the connection completed before the
            timeout expired; else, false is returned and the
            connection may or may not have succeeded
        :rtype: bool

        """

        self.logger.debug('Connecting %s to %s', self.__class__.__name__, addr)

        if self.socket and addr == self.addr:
            # Already connected.
            return True

        if self.socket:
            self.socket.close()

        ctx = zmq.Context.instance()
        self.socket = ctx.socket(self.SOCKET_TYPE)
        self.socket.linger = 0

        if config.CURVE_ENABLED:
            proxy_public_key, _ = auth.load_certificate(config.CURVE_PROXY_PUBLIC_KEY_FILE)
            agent_public_key, agent_secret_key = auth.load_certificate(config.CURVE_AGENT_SECRET_KEY_FILE)
            self.socket.curve_serverkey = proxy_public_key
            self.socket.curve_secretkey = agent_secret_key
            self.socket.curve_publickey = agent_public_key

        strategy = strategy or DEFAULT_STRATEGY
        set_fields(self.socket, **kwargs)

        self.addr = addr
        strategy.before_connect(self.socket, timeout_ms)
        if self.addr[0:3] == 'ipc':
            file_path = self.addr[6:]
            if os.path.exists(file_path) and not validate_file_permissions(file_path, 0o744):
                os.chmod(file_path, 0o744)
        self.socket.connect(self.addr)
        return strategy.after_connect(self.socket, timeout_ms)

    def disconnect(self):
        self.addr = None

    def wrap_message(self, msg):
        """Wrap a message in the correct envelope.

        This is done automatically by the ``send`` method.

        :param mapping msg:
        :return: the wrapped protobuf
        :rtype: a protobuf message

        """
        return pb_from_dict(ASyncRequest(), msg)

    def parse_response(self, serialized):
        """Parse a response.

        """
        raise NotImplementedError('parse_response not implemented in BaseTransport')

    def send(self, msg, flags=0):
        protobuf_msg = self.wrap_message(msg)
        self.logger.debug('sent protobuf {}'.format(protobuf_msg))
        return self.send_protobuf(protobuf_msg, flags=flags)

    def send_protobuf(self, protobuf_msg, flags=0):
        serialized = serialize_message(protobuf_msg)
        msg_parts = (b'AsyncReqRouter', b'', serialized)
        return self.socket.send_multipart(msg_parts, flags=flags)

    def _recv(self, flags):
        parts = self.socket.recv_multipart(flags=flags)
        return parts[2]

    def recv(self, timeout_ms=None, flags=zmq.NOBLOCK):
        if timeout_ms is not None:
            if timeout_ms <= 0:
                flags &= ~zmq.NOBLOCK
            elif not self.socket.poll(timeout_ms):
                return None

        try:
            serialized = self._recv(flags=flags)
            return self.parse_response(serialized)
        except zmq.Again:
            return None


class ControlTransport(BaseTransport):
    SOCKET_TYPE = zmq.REQ

    def send(self, msg, flags=0):
        # Mask the controller key while printing to avoid accesskey being shown
        masked_message = msg.copy()
        masked_message['accountAccessKey'] = '[****]'
        masked_protobuf_msg = self.wrap_message(masked_message)
        self.logger.debug('sent protobuf {}'.format(masked_protobuf_msg))
        protobuf_msg = self.wrap_message(msg)
        return self.send_protobuf(protobuf_msg, flags=flags)

    def connect(self, addr, timeout_ms=100, strategy=None, **kwargs):
        super(ControlTransport, self).connect(addr, timeout_ms, strategy=PollOutConnectionStrategy(), **kwargs)

    def wrap_message(self, msg):
        return pb_from_dict(StartNodeRequest(), msg)

    def parse_response(self, serialized):
        return parse_message(StartNodeResponse(), serialized)

    def send_protobuf(self, protobuf_msg, flags=0):
        serialized = serialize_message(protobuf_msg)
        msg_parts = (b'', serialized)
        return self.socket.send_multipart(msg_parts, flags=flags)

    def _recv(self, flags):
        parts = self.socket.recv_multipart(flags=flags)
        return parts[1]


class ConfigTransport(BaseTransport):
    def wrap_message(self, msg):
        return pb_from_dict(ASyncRequest(), {'type': ASyncRequest.CONFIG, 'configReq': msg})

    def parse_response(self, serialized):
        return parse_message(ConfigResponse(), serialized)


class InfoTransport(BaseTransport):
    def wrap_message(self, msg):
        return pb_from_dict(ASyncRequest(), {'type': ASyncRequest.BTINFO, 'btInfoReq': msg})

    def parse_response(self, serialized):
        return parse_message(BTInfoResponse(), serialized)


class ReportingTransport(BaseTransport):
    SOCKET_TYPE = zmq.PUB

    TYPE_BT_DETAILS = ASyncMessage.BTDETAILS
    TYPE_SELF_RERESOLUTION = ASyncMessage.SELFRERESOLUTION
    TYPE_PROCESS_SNAPSHOT = ASyncMessage.PROCESSSNAPSHOT
    TYPE_CUSTOM_METRIC = ASyncMessage.CUSTOMMETRIC

    def connect(self, addr, timeout_ms=100, strategy=None, **kwargs):
        super(ReportingTransport, self).connect(addr, timeout_ms, strategy=PollOutConnectionStrategy(), **kwargs)

    def wrap_message(self, msg):
        return pb_from_dict(ASyncMessage(), msg)

    def recv(self, timeout_ms=None, flags=0):
        raise NotImplementedError('reporting transport cannot receive')

    def send_custom_metric(self, msg, flags=0):
        """Send a custom metric to the proxy.

        Parameters
        ----------
        msg : mapping
            A dict containing custom metric to send.

        Other Parameters
        ----------------
        flags : int
            Flags to pass to the underlying ZeroMQ `send` method.

        Returns
        -------
        bool
            True if the send was successful, else false.

        """
        return self.send({'type': self.TYPE_CUSTOM_METRIC, 'customMetric': msg}, flags=flags)

    def send_bt_details(self, msg, flags=0):
        """Send BT details to the proxy.

        Parameters
        ----------
        msg : mapping
            A dict of the BT details to send.

        Other Parameters
        ----------------
        flags : int
            Flags to pass to the underlying ZeroMQ `send` method.

        Returns
        -------
        bool
            True if the send was successful, else false.

        """
        return self.send({'type': self.TYPE_BT_DETAILS, 'btDetails': msg}, flags=flags)

    def send_reresolution(self, msg, flags=0):
        """Send a self re-resolution message to the proxy.

        Parameters
        ----------
        msg : mapping
            A dict of the re-resolution information to send.

        Other Parameters
        ----------------
        flags : int
            Flags to pass to the underlying ZeroMQ `send` method.

        Returns
        -------
        bool
            True if the send was successful, else false.

        """
        return self.send({'type': self.TYPE_SELF_RERESOLUTION, 'selfReResolution': msg}, flags=flags)

    def send_process_snapshot(self, msg, flags=0):
        """Send a process snapshot to the proxy.

        Parameters
        ----------
        msg : mapping
            A dict containing the process snapshot to send.

        Other Parameters
        ----------------
        flags : int
            Flags to pass to the underlying ZeroMQ `send` method.

        Returns
        -------
        bool
            True if the send was successful, else false.

        """
        return self.send({'type': self.TYPE_PROCESS_SNAPSHOT, 'processSnapshot': msg}, flags=flags)

    def send_protobuf(self, protobuf_msg, flags=0):
        serialized = serialize_message(protobuf_msg)
        return self.socket.send(serialized, flags=flags)
