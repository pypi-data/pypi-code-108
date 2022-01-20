"""Functions to read and parse osef files/streams."""
import socket
import time
import traceback
from collections import deque
from itertools import islice
from struct import Struct
from typing import Any, Iterable, Optional, Tuple, Iterator
from urllib.parse import urlparse

from osef import types
from osef._logger import osef_logger
from osef.constants import _Tlv, _TreeNode, _STRUCT_FORMAT

TCP_TIMEOUT = 3


# -- Public functions --
class OsefStream:
    """Context manager class to open file path or tcp socket, then read its values.

    :param path: path to osef file or TCP stream if path has form *tcp://hostname:port*
    The sever may close the socket if client is too late.
    """

    TIMEOUT = 2

    def __init__(self, path: str):
        self._path = path
        self._parsed_path = urlparse(self._path)
        self._io_stream = None
        self.is_tcp = False

    def __enter__(self):
        if self._parsed_path.scheme == "tcp":
            self.is_tcp = True
            self.open_socket()
            return self
        self._io_stream = open(self._path, "rb")  # pylint: disable=consider-using-with
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._io_stream.close()

    def read(self, size: int = 4096) -> bytes:
        """Read `size` bytes from file or socket.

        :param size: of binary value to be read
        :raise EOFError: if no value can be read or if it is empty.
        :return: Read binary value
        """
        if self.is_tcp:
            try:
                msg = self._io_stream.recv(size)
            except socket.timeout:
                osef_logger.warning("Receive timeout. Closing socket.")
                self._io_stream.close()
                msg = None
            except ConnectionResetError:
                osef_logger.warning("Socket reset error. Closing socket.")
                self._io_stream.close()
                msg = None
            return msg

        return self._io_stream.read(size)

    def open_socket(self, auto_reconnect: bool = True):
        """Open tcp socket on provided path.
        Tries to connect again if the connection fails
        """
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Count the retries, to avoid flooding the log
        retry = 0

        while True:
            try:
                tcp_socket.settimeout(TCP_TIMEOUT)
                tcp_socket.connect(
                    (self._parsed_path.hostname, self._parsed_path.port or 11120)
                )
                break
            except ConnectionRefusedError:
                error_string = "Connection refused."
            except TimeoutError:
                error_string = "Timeout on TCP connection."
            except OSError as os_error:
                error_string = f"Error during connection: {os_error}."
            if retry % 100 == 0:
                osef_logger.error(error_string)

            if not auto_reconnect:
                break
            if retry % 100 == 0:
                osef_logger.warning("Retrying to connect ...")
            retry = retry + 1
            time.sleep(0.005)

        self._io_stream = tcp_socket


def iter_file(osef_stream: OsefStream, auto_reconnect: bool = True) -> Iterator[_Tlv]:
    """Iterator function to iterate over each frame in osef file.

    :param osef_stream: opened binary file containing tlv frames.
    :param auto_reconnect: enable reconnection for tcp connections.
    :return frame_tlv: next tlv frame of the osef file.
    """
    while True:
        try:
            frame_tlv = read_next_tlv(osef_stream)
        except EOFError:
            if auto_reconnect and osef_stream.is_tcp:
                osef_logger.warning("Connection lost: reopening socket")
                osef_stream.open_socket(auto_reconnect)
                continue
            break
        except Exception:  # pylint: disable=broad-except
            osef_logger.error(
                "Error: cannot read next Tlv from file (malformed Tlv?).\n"
                + f"Details: {traceback.format_exc()}"
                + "\n"
            )
            break

        yield frame_tlv


def get_tlv_iterator(
    opened_file: OsefStream,
    first: int = None,
    last: int = None,
    auto_reconnect: bool = True,
) -> Iterable[_Tlv]:
    """Get an iterator to iterate over each tlv frame in osef file.

    :param opened_file: opened binary file containing tlv frames.
    :param first: iterate only on N first frames of file.
    :param last: iterate only on M last frames of file.
    Can be used with first to get the range (N-M) -> N
    :param auto_reconnect: enable reconnection for tcp connections.
    :return: tlv frame iterator
    """
    if first is None and last is None:
        return enumerate(iter_file(opened_file, auto_reconnect))
    return deque(islice(enumerate(iter_file(opened_file, auto_reconnect)), first), last)


def build_tree(tlv: _Tlv) -> _TreeNode:
    """Recursive function to get a tree from a raw Tlv frame

    :param tlv: raw tlv frame read from file.
    :return: tree representation of the tlv frame
    """
    # If we know this type is an internal node (not a leaf)
    if tlv.type in types.outsight_types and isinstance(
        types.outsight_types[tlv.type].node_info, types.InternalNodeInfo
    ):
        read = 0
        children = []
        while read < tlv.length:
            sub_tlv, sub_size = _parse_tlv_from_blob(tlv.value, read)
            sub_tree = build_tree(sub_tlv)
            children.append(sub_tree)
            read += sub_size
        return _TreeNode(tlv.type, children, None)
    return _TreeNode(tlv.type, None, tlv.value)


def unpack_value(value: bytes, leaf_info: types.LeafInfo, type_name: str = "") -> Any:
    """Unpack a leaf value to a python object (type depends on type of leaf).

    :param value: binary value to be unpacked.
    :param leaf_info: type info for unpacking and conversion to python object.
    :param type_name: (optional) provide type name
     to provide better feedback if an exception occurs
    :return: python object
    """
    try:

        if leaf_info.unpack_function is not None:
            return leaf_info.unpack_function(value)
        # unknown parser
        return value

    except Exception as err:
        raise type(err)(f'occurred while unpacking "{type_name}".') from err


def parse_to_dict(frame_tree: _TreeNode) -> dict:
    """Parse a whole frame tree to a python dictionary. All values of the tree will be unpacked.

    :param frame_tree: raw tree of a tlv frame.
    :return: dictionary with all values in osef frame.
    """
    type_name, subtree = _parse_raw_to_tuple(frame_tree)
    return {type_name: subtree}


def parse(
    path: str,
    first: Optional[int] = None,
    last: Optional[int] = None,
    auto_reconnect: bool = True,
) -> Iterator[dict]:
    """Iterator that opens and convert each tlv frame to a dict.

    :param path: path to osef file or TCP stream if path has form *tcp://hostname:port*
    :param first: iterate only on N first frames of file.
    :param last: iterate only on M last frames of file.
    Can be used with first to get the range (N-M) ... N
    :param auto_reconnect: enable reconnection for tcp connections.
    :return: next tlv dictionary
    """
    with OsefStream(path) as osef_stream:
        iterator = get_tlv_iterator(osef_stream, first, last, auto_reconnect)
        for _, tlv in iterator:
            raw_tree = build_tree(tlv)
            if raw_tree:
                yield parse_to_dict(raw_tree)


# -- Tlv Parsing --


def read_next_tlv(osef_stream: OsefStream) -> Optional[_Tlv]:
    """Read the next TLV from a binary stream (file or socket)"""
    # Read header
    struct = Struct(_STRUCT_FORMAT % 0)
    blob = _read_from_file(osef_stream, struct.size)
    # Parse Type and Length
    read_tlv = _Tlv._make(struct.unpack_from(blob))

    # Now that we know its length we can read the Value
    struct = Struct(_STRUCT_FORMAT % read_tlv.length)
    blob += _read_from_file(osef_stream, struct.size - len(blob))
    read_tlv = _Tlv._make(struct.unpack_from(blob))

    return read_tlv


def _align_size(size: int) -> int:
    """Returned aligned size from tlv size"""
    alignment_size = 4
    offset = size % alignment_size
    return size if offset == 0 else size + alignment_size - offset


def _read_from_file(osef_stream: OsefStream, byte_number: int) -> bytes:
    """Read given number of bytes from readable stream"""
    blob = b""
    while len(blob) < byte_number:
        blob_inc = osef_stream.read(byte_number - len(blob))
        # End of file
        if blob_inc is None or len(blob_inc) == 0:
            raise EOFError
        blob += blob_inc
    return blob


def _parse_tlv_from_blob(blob: bytes, offset=0) -> Tuple[_Tlv, int]:
    """Parse a TLV from a binary blob"""
    # Unpack a first time to get Type and Length
    struct = Struct(_STRUCT_FORMAT % 0)
    read_tlv = _Tlv._make(struct.unpack_from(blob, offset))

    # Then unpack the whole tlv
    struct = Struct(_STRUCT_FORMAT % read_tlv.length)
    read_tlv = _Tlv._make(struct.unpack_from(blob, offset))

    return read_tlv, _align_size(struct.size)


# -- OSEF parsed tree --


def _parse_raw_to_tuple(raw_tree: _TreeNode) -> Tuple[str, Any]:
    """Parse a raw TLV tree, using OSEF types"""
    osef_type, children, leaf_value = raw_tree

    # Get leaf type info
    type_info = types.get_type_info_by_id(osef_type)

    # For leaves or unknown, return value
    if isinstance(type_info.node_info, types.LeafInfo):
        return type_info.name, unpack_value(
            leaf_value, type_info.node_info, type_info.name
        )

    # For non-leaves, add each child to a dictionary
    tree = {}
    if type_info.node_info.type == list:
        tree = []

    for child in children:
        child_name, child_tree = _parse_raw_to_tuple(child)

        if type_info.node_info.type == dict:
            tree[child_name] = child_tree
        elif type_info.node_info.type == list:
            tree.append({child_name: child_tree})
        else:
            raise ValueError("Unsupported internal node type.")

    return type_info.name, tree
