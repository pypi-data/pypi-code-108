#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Communication protocol implementing an OPC UA connection.
This protocol is used to interface with the "Supercube" PLC from Siemens.
"""

import errno
import logging
from collections.abc import Iterable as IterableBase
from concurrent.futures import CancelledError, TimeoutError
from functools import wraps
from ipaddress import IPv4Address, IPv6Address
from socket import gaierror
from time import sleep
from typing import Iterable, Union, Optional

import asyncio
from asyncua import ua, sync
from asyncua.ua import NodeId, DataValue, UaError
from asyncua.ua.uaerrors import BadSubscriptionIdInvalid
from asyncua.ua.uatypes import Variant

from hvl_ccb.utils.validation import validate_and_resolve_host, validate_tcp_port
from .base import CommunicationProtocol, CommunicationException
from ..configuration import configdataclass

logger = logging.getLogger(__name__)


class Client(sync.Client):
    def __init__(self, url: str, timeout: int = 4):
        super().__init__(url, timeout)
        self.uaclient = self.aio_obj.uaclient

        self.aio_obj.session_timeout = 30000
        self.aio_obj.secure_channel_timeout = 30000

    # this method seems to be missing from the new sync client
    def get_objects_node(self):
        """
        Get Objects node of client. Returns a Node object.
        """
        return self.get_node(ua.TwoByteNodeId(ua.ObjectIds.ObjectsFolder))

    @sync.syncmethod
    def send_hello(self):
        pass

    @property
    def is_open(self):
        return self.aio_obj.uaclient.protocol is not None

    def disconnect(self):
        if self.is_open:
            self.tloop.post(self.aio_obj.disconnect())

        if self.close_tloop:
            self.tloop.stop()


class Server(sync.Server):
    # this method seems to be missing from the new sync client
    def get_objects_node(self):
        """
        Get Objects node of server. Returns a Node object.
        """
        return self.get_node(ua.TwoByteNodeId(ua.ObjectIds.ObjectsFolder))


class OpcUaSubHandler:
    """
    Base class for subscription handling of OPC events and data change events.
    Override methods from this class to add own handling capabilities.

    To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing.
    """

    def datachange_notification(self, node, val, data):
        logger.debug(f"OPCUA Datachange event: {node} to value {val}")

    def event_notification(self, event):
        logger.debug(f"OPCUA Event: {event}")


@configdataclass
class OpcUaCommunicationConfig:
    """
    Configuration dataclass for OPC UA Communciation.
    """

    #: Hostname or IP-Address of the OPC UA server.
    host: Union[str, IPv4Address, IPv6Address]

    #: Endpoint of the OPC server, this is a path like 'OPCUA/SimulationServer'
    endpoint_name: str

    #: Port of the OPC UA server to connect to.
    port: int = 4840

    #: object to use for handling subscriptions.
    sub_handler: OpcUaSubHandler = OpcUaSubHandler()

    #: Values are given as a `ua.CreateSubscriptionParameters` as these parameters
    #: are requested by the OPC server. Other values will lead to an automatic revision
    #: of the parameters and a warning in the opc-logger, cf. MR !173
    update_parameter: ua.CreateSubscriptionParameters = ua.CreateSubscriptionParameters(
        RequestedPublishingInterval=1000,
        RequestedLifetimeCount=300,
        RequestedMaxKeepAliveCount=22,
        MaxNotificationsPerPublish=10_000,
    )

    #: Wait time between re-trying calls on underlying OPC UA client timeout error
    wait_timeout_retry_sec: Union[int, float] = 1

    #: Maximal number of call re-tries on underlying OPC UA client timeout error
    max_timeout_retry_nr: int = 5

    def clean_values(self):
        if (
            min(
                self.update_parameter.RequestedPublishingInterval,
                self.update_parameter.RequestedLifetimeCount,
                self.update_parameter.RequestedMaxKeepAliveCount,
                self.update_parameter.MaxNotificationsPerPublish,
            )
            < 0
        ):
            raise ValueError(
                "Update period parameters for generating datachange events "
                "need to be positive numbers."
            )
        if self.wait_timeout_retry_sec <= 0:
            raise ValueError(
                "Re-try wait time (sec) on timeout needs to be a positive number."
            )
        if self.max_timeout_retry_nr < 0:
            raise ValueError(
                "Maximal re-tries count on timeout needs to be non-negative integer."
            )
        self.force_value("host", validate_and_resolve_host(self.host, logger))
        validate_tcp_port(self.port, logger)


class OpcUaCommunicationIOError(IOError, CommunicationException):
    """OPC-UA communication I/O error."""


class OpcUaCommunicationTimeoutError(OpcUaCommunicationIOError):
    """OPC-UA communication timeout error."""


#: current number of reopen tries on OPC UA connection error
_n_timeout_retry = 0


def _wrap_ua_error(method):
    """
    Wrap any `UaError` raised from a `OpcUaCommunication` method into
    `OpcUaCommunicationIOError`; additionally, log source error.

    :param method: `OpcUaCommunication` instance method to wrap
    :return: Whatever `method` returns
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):

        try:

            result = method(self, *args, **kwargs)

        except UaError as e:
            err_msg = "OPC UA client runtime error"
            logger.error(err_msg, exc_info=e)
            raise OpcUaCommunicationIOError(err_msg) from e

        except gaierror as e:
            err_msg = "Socket address error"
            logger.error(err_msg, exc_info=e)
            raise OpcUaCommunicationIOError(err_msg) from e

        except OSError as e:

            if e.errno == errno.EBADF:
                err_msg = "OPC UA client socket error"
            else:
                err_msg = "OPC UA client OS error"
            logger.error(err_msg, exc_info=e)
            raise OpcUaCommunicationIOError(err_msg) from e

        except (CancelledError, asyncio.CancelledError) as e:
            err_msg = "OPC UA client thread cancelled error"
            logger.error(err_msg, exc_info=e)
            raise OpcUaCommunicationIOError(err_msg) from e

        except (TimeoutError, asyncio.TimeoutError) as e:
            err_msg = "OPC UA client thread timeout error"
            logger.error(err_msg, exc_info=e)
            # try close, re-open and re-call
            global _n_timeout_retry
            _max_try_reopen = self.config.max_timeout_retry_nr
            if _n_timeout_retry < _max_try_reopen:
                sleep(self.config.wait_timeout_retry_sec)
                _n_timeout_retry += 1

                logger.info(
                    f"OPC UA client retry #{_n_timeout_retry}/#{_max_try_reopen}:"
                    f" {method}"
                )

                # note: nested re-tries use the global counter to stop on max limit
                result = wrapper(self, *args, **kwargs)
                # success => reset global counter
                _n_timeout_retry = 0

            else:
                # failure => reset global counter
                _n_timeout_retry = 0
                # raise from original timeout error
                raise OpcUaCommunicationTimeoutError from e

        return result

    return wrapper


def _require_ua_opened(method):
    """
    Check if `asyncua.client.ua_client.UaClient` socket is opened and raise an
    `OpcUaCommunicationIOError` if not.
    Check if `opcua.client.protocol.UASocketProtocol` socket is opened and raise an
    `OpcUaCommunicationIOError` if not.

    NOTE: this checks should be implemented downstream in
    `asyncua.client.ua_client.UaClient` methods;
    currently you get `AttributeError: 'NoneType'
    object has no attribute ...`.

    :param method: `OpcUaCommunication` instance method to wrap
    :return: Whatever `method` returns
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # BLAH: this checks should be implemented downstream in
        # `asyncua.client.ua_client.UaClient` methods
        if not (self._client and self._client.is_open):
            err_msg = f"Client's socket is not set in {str(self)}. Was it opened?"
            logger.error(err_msg)
            raise OpcUaCommunicationIOError(err_msg)
        return method(self, *args, **kwargs)

    return wrapper


class OpcUaCommunication(CommunicationProtocol):
    """
    Communication protocol implementing an OPC UA connection.
    Makes use of the package python-opcua.
    """

    def __init__(self, config) -> None:
        """
        Constructor for OpcUaCommunication.

        :param config: is the configuration dictionary.
        """

        super().__init__(config)

        self._client: Optional[Client] = None

        # the objects node exists on every OPC UA server and are root for all objects.
        self._objects_node: Optional[sync.SyncNode] = None

        # subscription handler
        self._sub_handler = self.config.sub_handler

        # subscription object
        self._subscription: Optional[sync.Subscription] = None

    @staticmethod
    def config_cls():
        return OpcUaCommunicationConfig

    def _create_client(self) -> Client:
        conf = self.config

        url = f"opc.tcp://{conf.host}:{conf.port}/{conf.endpoint_name}"

        logger.info(f"Create OPC UA client to URL: {url}")

        return Client(url)

    @_wrap_ua_error
    def open(self) -> None:
        """
        Open the communication to the OPC UA server.

        :raises OpcUaCommunicationIOError: when communication port cannot be opened.
        """

        logger.info("Open connection to OPC server.")
        with self.access_lock:
            try:
                self._client = self._create_client()
                self._client.connect()
                # in example from opcua,
                # load_type_definitions() is called after connect().
                # However, this raises ValueError when connecting to Siemens S7,
                # and no problems are detected omitting this call.
                # self._client.load_type_definitions()
                self._objects_node = self._client.get_objects_node()
                self._subscription = self._client.create_subscription(
                    self.config.update_parameter, self._sub_handler
                )
            except BaseException as e:
                # If the client was not opened properly due to a bad connection,
                # using the keyboard or logging out, you need to call ``self.close()``
                # to cleanup threads and avoid potential thread locks issues.
                logger.error(str(e), exc_info=e)
                self.close()
                raise e

    @property
    def is_open(self) -> bool:
        """
        Flag indicating if the communication port is open.

        :return: `True` if the port is open, otherwise `False`
        """
        if self._client:
            open_called = self._objects_node or self._subscription
            if open_called:
                try:
                    self._client.send_hello()
                    return True
                except UaError as e:
                    logger.info(f"Sending hello returned UA error: {str(e)}")
                    # try cleanup in case connection was opened before but now is lost
                    if open_called:
                        self.close()
        return False

    @_wrap_ua_error
    def close(self) -> None:
        """
        Close the connection to the OPC UA server.
        """

        logger.info("Close connection to OPC server.")
        with self.access_lock:
            if self._subscription:
                try:
                    self._subscription.delete()
                except BadSubscriptionIdInvalid as e:
                    logger.error(str(e), exc_info=e)
                self._subscription = None
            if self._objects_node:
                self._objects_node = None
            if self._client:
                self._client.disconnect()
                self._client = None

    @_require_ua_opened
    @_wrap_ua_error
    def read(self, node_id, ns_index):
        """
        Read a value from a node with id and namespace index.

        :param node_id: the ID of the node to read the value from
        :param ns_index: the namespace index of the node
        :return: the value of the node object.
        :raises OpcUaCommunicationIOError: when protocol was not opened or can't
            communicate with a OPC UA server
        """

        with self.access_lock:
            return self._client.get_node(
                NodeId(Identifier=node_id, NamespaceIndex=ns_index)
            ).get_value()

    @_require_ua_opened
    @_wrap_ua_error
    def write(self, node_id, ns_index, value) -> None:
        """
        Write a value to a node with name ``name``.

        :param node_id: the id of the node to write the value to.
        :param ns_index: the namespace index of the node.
        :param value: the value to write.
        :raises OpcUaCommunicationIOError: when protocol was not opened or can't
            communicate with a OPC UA server
        """
        # make mypy happy; check was done in `_require_ua_opened` decorator
        assert self._client is not None

        with self.access_lock:
            node_id_name = NodeId(Identifier=node_id, NamespaceIndex=ns_index)
            node = self._client.get_node(node_id_name)
            variant_type = node.get_data_type_as_variant_type()
            node.set_value(DataValue(Variant(value, variant_type)))

    @_require_ua_opened
    @_wrap_ua_error
    def init_monitored_nodes(
        self, node_id: Union[object, Iterable], ns_index: int
    ) -> None:
        """
        Initialize monitored nodes.

        :param node_id: one or more strings of node IDs; node IDs are always casted
            via `str()` method here, hence do not have to be strictly string objects.
        :param ns_index: the namespace index the nodes belong to.
        :raises OpcUaCommunicationIOError: when protocol was not opened or can't
            communicate with a OPC UA server
        """
        # make mypy happy; check was done in `_require_ua_opened` decorator
        assert self._client is not None

        if not self._subscription:
            err_msg = f"Missing subscription in {str(self)}. Was it opened?"
            logger.error(err_msg)
            raise OpcUaCommunicationIOError(err_msg)

        ids: Iterable[object] = (
            node_id
            if not isinstance(node_id, str) and isinstance(node_id, IterableBase)
            else (node_id,)
        )

        nodes = []
        for id_ in ids:
            nodes.append(
                self._client.get_node(
                    NodeId(Identifier=str(id_), NamespaceIndex=ns_index)
                )
            )

        with self.access_lock:
            self._subscription.subscribe_data_change(nodes)
