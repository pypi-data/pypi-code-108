import socket
from functools import wraps
from typing import List, Optional, Tuple

from centaur._.pyvmps.communicator.exceptions import SendMessageException
from centaur._.pyvmps.communicator.utils import check_last_part
from centaur._.pyvmps.cfg.config import GowebProtocolConst
from centaur._.pyvmps.logger.get_logger import get_logger

_logger = get_logger(__name__)


def timeout_control(sc_inst, timeout: float = -1):
    """timeout_control - decorator used to set socket timeout value for 1 socket operation

    :param sc_inst: socket control instance
    :param timeout: timeout to set. If timeout==-1, use default timeout (None)
    :type timeout: float
    """

    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if timeout != -1:
                prev_timeout: Optional[float] = sc_inst.s.gettimeout()
                sc_inst.s.settimeout(timeout)
                _logger.debug("SETTING TIMEOUT=%s, PREV_TIMEOUT=%s", timeout, prev_timeout)
                try:
                    res = f(*args, **kwargs)
                    sc_inst.s.settimeout(prev_timeout)
                    return res
                except Exception:
                    # catch to reset socket timeout to previous timeout then reraise
                    sc_inst.s.settimeout(prev_timeout)
                    raise

            else:
                return f(*args, **kwargs)

        return inner

    return decorator


def _apply_protocol(_payload: bytes, i_of_n: bytes) -> bytes:
    # jit check
    if isinstance(i_of_n, str):
        i_of_n = i_of_n.encode()
    if isinstance(_payload, str):
        _payload = _payload.encode()
    msg_body: bytes = i_of_n + _payload
    msg_header: bytes = str(len(msg_body)).zfill(GowebProtocolConst.MSG_HEADER_LENGTH).encode()
    return msg_header + msg_body


def _num_parts(_payload) -> Tuple[List[bytes], List[bytes]]:
    # NOTE: for now just assume payload can fit into 1 uds message
    return [_payload], [GowebProtocolConst._PY_LAST_PKT_FLAG]


# def _send(socket, payload: bytes, timeout: int = -1):
def _send(io_stream, payload: bytes, timeout: int = -1):
    """send byte string to uds peer

    From https://docs.python.org/3.6/howto/sockets.html#using-a-socket
    and https://docs.python.org/3.6/library/socket.html#socket.socket.sendall

    Use socket.sendall(bytes[, flags]), send all data and return None on success or raise exception
    Caller is expected to catched raised exception

    Raises: SendMessageException

    :param payload: payload to send
    :type payload: bytes
    :param timeout: timeout to set on socket connection
    :type timeout: int
    """

    def __send(_payload):
        try:
            io_stream.write(_payload)
            io_stream.flush()
            _logger.debug("socket_control|send|payload_len=%s", len(payload))
        except Exception as e:
            _logger.exception("error sending payload")
            raise SendMessageException("Error sending payload") from e

    payload_parts, parts = _num_parts(payload)
    for p, i_of_n in zip(payload_parts, parts):
        __send(_apply_protocol(p, i_of_n))


def _receive(io_stream, timeout: float = -1) -> bytes:
    """receive calls socket.recv() internally and applies a custom protocol
    Calls recv() n times depending on number of parts indicated in message

    :param timeout: USE WITH CAUTION. Exceptions raised when reading to file type may result in the buffer being
    in an inconsistent state. Defaults to -1 (Blocking)
    :type timeout: float
    :rtype: bytes
    """

    def __read_one_msg() -> Tuple[bytes, bytes]:
        msg: bytes = b""
        length_bytes = io_stream.read(GowebProtocolConst.MSG_HEADER_LENGTH)
        if length_bytes == b"":
            _logger.exception("EOFError")
            raise EOFError("Error reading from stream")

        payload_length: int = int(length_bytes)
        _logger.debug("receive|length_to_read=%s", payload_length)
        # io_stream = socket.makefile(mode="b")
        msg_body: bytes = io_stream.read(payload_length)
        last_pkt_flag: bytes = msg_body[: GowebProtocolConst.X_OF_PARTS_LENGTH]
        actual_body = msg_body[GowebProtocolConst.X_OF_PARTS_LENGTH :]
        msg += actual_body
        _logger.debug("receive|msg_len=%s,last_pkt_flag=%s", len(msg), last_pkt_flag)
        return msg, last_pkt_flag

    def __receive() -> bytes:

        final_msg, flag = __read_one_msg()
        while not check_last_part(flag):
            _logger.debug("receive|not last part")
            msg, flag = __read_one_msg()
            final_msg += msg
        _logger.debug("last part")
        return final_msg

    msg = __receive()
    _logger.debug("msg_received")
    return msg


class SocketControl:
    """SocketControl is the baselayer that will communicate with the go engine and pass data to the upper layers"""

    def __init__(self, address: str):
        self.s = socket.socket(family=socket.AF_UNIX)  # pylint: disable=no-member
        self.address = address
        self.registered: bool = False
        self.s.settimeout(None)
        self.connect()
        self.r_stream = self.s.makefile("rb")
        self.w_stream = self.s.makefile("wb")

    def connect(self):
        @timeout_control(self, 0)
        def _connect():
            _logger.info("socket_control|connect_to_goweb|address=%s", self.address)
            self.s.connect(self.address)
            _logger.info("socket connected to=%s", self.s.getpeername())

        _connect()

    def shutdown(self):
        self.r_stream.flush()
        self.r_stream.close()

        self.w_stream.flush()
        self.w_stream.close()
        self.s.close()

    def send(self, payload: bytes, timeout: int = -1):
        """send byte string to uds peer

        From https://docs.python.org/3.6/howto/sockets.html#using-a-socket
        and https://docs.python.org/3.6/library/socket.html#socket.socket.sendall

        Use socket.sendall(bytes[, flags]), send all data and return None on success or raise exception
        Caller is expected to catched raised exception

        Raises: SendMessageException

        :param payload: payload to send
        :type payload: bytes
        :param timeout: timeout to set on socket connection
        :type timeout: int
        """
        _send(self.w_stream, payload, timeout)

    def receive(self, timeout: float = -1) -> bytes:
        """receive calls socket.recv() internally and applies a custom protocol
        Calls recv() n times depending on number of parts indicated in message

        :param timeout:
        :type timeout: float
        :rtype: bytes
        """

        # return _receive(self.s, timeout)
        return _receive(self.r_stream, timeout)


if __name__ == "__main__":
    address = "/tmp/pyvmp-uds/socket.sock"
    sc = SocketControl(address)
