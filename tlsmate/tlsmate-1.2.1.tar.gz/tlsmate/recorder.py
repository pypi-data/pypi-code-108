# -*- coding: utf-8 -*-
"""Module with a class for recording a tls connection
"""
# import basic stuff
import enum
import datetime
import time
from typing import List, Any, Dict, Tuple, Optional

# import own stuff
import tlsmate.config as conf
import tlsmate.tls as tls
import tlsmate.utils as utils


# import other stuff
import requests


class RecorderState(enum.Enum):
    """States for the recorder
    """

    INACTIVE = 0
    RECORDING = 1
    REPLAYING = 2


class SocketEvent(enum.Enum):
    """Events that might occur when waiting for socket data
    """

    TIMEOUT = 0
    DATA = 1
    CLOSURE = 2


class Recorder(object):
    """Class implementing a recorder mechanism.

    The purpose of the class is to have a build-in mechanism for unit testing. It works
    by providing hooks to all external interfaces. `External interface` means messages
    sent and received via the socket as well as numbers generated randomly.

    If inactive, the recorder has no functional impact on the rest of tlsmate.
    When recording, the recorder stores all data which are passing the interfaces,
    and they are `recorded`, i.e., they are stored in the recorder object. This mode
    is used to record a unit test case (which can be as complex as a complete scan of
    a server). After the recoding is finished, the complete recorder object is
    serialized to a YAML file.
    When replaying (normally triggered by pytest), the recorder object is deserialized
    from the file, and all recorded data is injected when the external interfaces
    are used. This way an EXACT clone of the connection(s) is/are executed. The
    replayed test case uses the same keying material as well, it is a `byte-to-byte`
    copy. Of course, all data sent over external interfaces are checked, and any
    deviation with the previously recorded data will let the test case fail.
    Note, that even after some cryptographic operations the recorder is hooked in, this
    allows easier debugging in case a replayed test deviates from the recorded twin.
    """

    _attr = {
        "client_random": bytes,
        "server_random": bytes,
        "pre_master_secret": bytes,
        "master_secret": bytes,
        "private_key": bytes,
        "client_write_mac_key": bytes,
        "server_write_mac_key": bytes,
        "client_write_key": bytes,
        "server_write_key": bytes,
        "client_write_iv": bytes,
        "server_write_iv": bytes,
        "verify_data_finished_rec": bytes,
        "verify_data_finished_calc": bytes,
        "msg_digest_finished_rec": bytes,
        "msg_digest_finished_sent": bytes,
        "verify_data_finished_sent": bytes,
        "ec_seed": int,
        "pms_rsa": bytes,
        "rsa_enciphered": bytes,
        "x_val": bytes,
        "y_val": int,
        "openssl_command": str,
        "early_secret": bytes,
        "early_tr_secret": bytes,
        "msg_digest_tls13": bytes,
        "binder": bytes,
        "binder_key": bytes,
        "finished_key": bytes,
        "msg_without_binders": bytes,
        "hmac_algo": str,
        "timestamp": float,
        "datetime": datetime.datetime,
        "msg_sendall": bytes,
        "msg_recv": "msg_recv",
        "crl_url": str,
        "crl": bytes,
        "signature": bytes,
        "trust_store": str,
        "client_auth": bool,
        "client_key_chain": "client_key_chain",
        "grease": int,
        "response": "response",
    }

    def __init__(self, config: Optional[conf.Configuration] = None) -> None:
        self.reset()
        self._delay = True
        if config:
            self._delay = config.get("recorder_delay")

    def reset(self) -> None:
        """Reset the recorder to an initial state.
        """
        self._state = RecorderState.INACTIVE
        self._add_delay = None
        self.data: Dict[str, Any] = {}
        for key in self._attr.keys():
            self.data[key] = []

    @staticmethod
    def _serialize_val(val, val_type):
        """Convert values to JSON/YAML serializable types

        Arguments:
            val: the value to convert
            val_type: the type of value

        Returns:
            ret: the converted value
        """

        if val_type is bytes:
            return val.hex()

        elif val_type is datetime.datetime:
            return val.timestamp()

        elif val_type == "msg_recv":
            timeout, event_type, data = val
            if data is not None:
                data = data.hex()

            return [timeout, event_type.value, data]

        elif val_type == "response":
            timeout, event_type, data = val
            if data is not None:
                data = [data.ok, data.content.hex(), data.status_code]

            return [timeout, event_type.value, data]

        return val

    @staticmethod
    def _deserialize_val(val, val_type):
        """Convert a serialized type to the original type

        Arguments:
            val: the value to convert
            val_type: the type of value

        Returns:
            ret: the converted value
        """

        if val_type is bytes:
            return bytes.fromhex(val)

        elif val_type is datetime.datetime:
            return datetime.datetime.fromtimestamp(val)

        elif val_type == "msg_recv":
            timout, event_type, data = val
            event_type = SocketEvent(event_type)
            if data is not None:
                data = bytes.fromhex(data)

            val = (timout, event_type, data)

        elif val_type == "response":
            timout, event_type, data = val
            event_type = SocketEvent(event_type)
            if data is not None:
                data[1] = bytes.fromhex(data[1])
            val = (timout, event_type, data)

        return val

    def _store_value(self, name, value):
        self.data[name].append(self._serialize_val(value, self._attr[name]))

    def _unstore_value(self, name):
        if not self.data[name]:
            return None

        return self._deserialize_val(self.data[name].pop(0), self._attr[name])

    def deactivate(self) -> None:
        """Deactivate the recorder.
        """

        self._state = RecorderState.INACTIVE

    def record(self) -> None:
        """Activate the recorder to record a test case.
        """

        self._state = RecorderState.RECORDING

    def replay(self) -> None:
        """Activate the recorder to replay a test case.
        """

        self._state = RecorderState.REPLAYING

    def is_injecting(self) -> bool:
        """Check if the recorder is currently replaying (i.e. injecting data)

        Returns:
            True if the recorder is replaying
        """

        return self._state is RecorderState.REPLAYING

    def is_recording(self) -> bool:
        """Check if the recorder is currently recording.

        Returns:
            True, if the recorder is recording
        """

        return self._state is RecorderState.RECORDING

    def get_trust_store(self) -> List[str]:
        """Provide the data for the trust store

        Returns:
            A list of certificates in the trust store. These are strings
            representing the certificates in DER-format.
        """

        return self.data["trust_store"]

    def trace_client_auth(self, cl_auth: Tuple[str, List[str]]) -> None:
        """Add a set of client authentication data to the recorder.

        Arguments:
            cl_auth: the key and the certificate chain to add to the recorder.
                Both must be provided as strings.
        """

        if self._state is RecorderState.RECORDING:
            self.data["client_key_chain"].append(cl_auth)

    def get_client_auth(self) -> List[Tuple[bytes, bytes]]:
        """Provide access to a list of client authentication sets.

        Returns:
            list: A list of (key/cert-chain) pairs.
        """

        return self.data["client_key_chain"]

    def trace_socket_recv(
        self, timeout: float, event_type: SocketEvent, data: Optional[bytes] = None
    ) -> None:
        """Trace a message received from a socket (if state is recording).

        Arguments:
            timeout: the timeout after that the event occurred in seconds
            event_type: the event that occurred
            data: the message in raw format (if event_type is data)
        """

        if self._state is RecorderState.RECORDING:
            if self._add_delay is not None:
                timeout += self._add_delay
                self._add_delay = None

            self._store_value("msg_recv", (timeout, event_type, data))

    def inject_socket_recv(self) -> Optional[bytes]:
        """If the recorder is replaying, inject the previously recorded message.

        Returns:
            the message previously recorded
        """

        if self._state is RecorderState.REPLAYING:
            timeout, event_type, data = self._unstore_value("msg_recv")
            if self._delay:
                time.sleep(timeout)

            if event_type is SocketEvent.CLOSURE:
                raise tls.TlsConnectionClosedError

            elif event_type is SocketEvent.TIMEOUT:
                raise tls.TlsMsgTimeoutError

            return data

        return None

    def additional_delay(self, delay: float) -> None:
        """Indicate that there is an additional delay when waiting to inject a message.

        Arguments:
            delay: The additional delay to take into account when injecting a
                received message the next time.
        """

        if self._add_delay is None:
            self._add_delay = delay  # type: ignore

        else:
            self._add_delay += delay

    def trace_socket_sendall(self, msg: bytes) -> bool:
        """Interface for the sendall socket function.

        Arguments:
            msg: the message to send over the socket

        Returns:
            True, if the message is sent externally.
        """

        if self._state is RecorderState.RECORDING:
            self._store_value("msg_sendall", msg)

        return self._state != RecorderState.REPLAYING

    def trace(self, **kwargs: Any) -> None:
        """Interface to trace any data

        Arguments:
            **kwargs: the name and value to trace
        """

        if self._state is RecorderState.INACTIVE:
            return

        name, val = kwargs.popitem()
        if name in self._attr:
            if self._state is RecorderState.REPLAYING:
                assert val == self._unstore_value(name)

            else:
                self._store_value(name, val)

    def inject(self, **kwargs: Any) -> Any:
        """Interface to potentially inject recorded data

        If recording, the data provided is stored in the recorder object.
        If replaying, the data previously recorded is returned.

        Arguments:
            **kwargs: the name and value of the data

        Returns:
            If recording: the data provided via kwargs, if replaying: the data
            previously recorded.
        """

        name, val = kwargs.popitem()
        if self._state is RecorderState.INACTIVE:
            return val

        if name in self._attr:
            if self._state is RecorderState.REPLAYING:
                val = self._unstore_value(name)

            else:
                self._store_value(name, val)

        return val

    def inject_response(self) -> Optional[Any]:
        """Inject a :obj:`requests.Response` object

        Only minimal ducktyping is supported.

        Returns:
            an object with the attributes ok, status_code and content
        """

        class _Response:
            pass

        if self._state is RecorderState.REPLAYING:
            timeout, event_type, data = self._unstore_value("response")
            if self._delay:
                time.sleep(timeout)

            if event_type is SocketEvent.CLOSURE:
                raise Exception

            elif event_type is SocketEvent.TIMEOUT:
                raise requests.Timeout

            response = _Response()
            response.ok, response.content, response.status_code = data  # type: ignore
            return response

        return None

    def trace_response(
        self, timeout: float, event_type: SocketEvent, data: Optional[bytes] = None
    ) -> None:
        """Trace the result of a post/get/... request.

        Arguments:
            timeout: the timeout after which the response was received.
            event_type: the event that occurred
            data: the response object from which only the most relevant
                attributes are recorded (ok, status_code, content). Only
                present if event_type is SocketEvent.DATA.
        """

        if self._state is RecorderState.RECORDING:
            self._store_value("response", (timeout, event_type, data))

    def serialize(self, filename: str) -> None:
        """Serialize the recorded data to a file using YAML

        Arguments:
            filename: the file name to store the data in
        """

        utils.serialize_data(self.data, file_name=filename, replace=False, indent=2)

    def deserialize(self, filename: str) -> None:
        """Deserialize the recorded data from a file

        Arguments:
            filename (str): the file name to deserialize the data from
        """

        self.data = utils.deserialize_data(filename)

    def get_timestamp(self) -> datetime.datetime:
        """Return an appropriate timestamp

        Returns:
            datetime.datetime: the timestamp. If the recorder is injecting, it is the
            recorded timestamp, else the current time (which is recorded, if the
            recorder is active).
        """
        if self.is_injecting():
            return self.inject(datetime=None)

        else:
            timestamp = datetime.datetime.now()
            self.trace(datetime=timestamp)
            return timestamp
