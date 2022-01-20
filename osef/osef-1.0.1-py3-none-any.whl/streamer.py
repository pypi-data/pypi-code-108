"""Tools to stream osef on a TCP socket."""
import pathlib
import socket
import struct
import time

from osef import parser
from osef.parser import build_tree, parse_to_dict


def stream_osef_file(
    file_path: str, ip_address: str, port: int = 11120, repeat: bool = False
):
    """Stream an osef file on a TCP socket with the right inter frame timing.

    :param file_path: local path to the osef file to stream.
    :param ip_address: hostname or IP address
    :param port: to be used (typically 11120)
    :param repeat: stream the osef in a loop.
    """
    filepath = pathlib.Path(file_path)
    if not filepath.is_file():
        raise FileNotFoundError(f"File {file_path} could not be found.")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # to avoid: [Errno 98] Address already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # connect socket to client
        server_socket.bind((ip_address, port))
        server_socket.listen(1)
        client_socket, _ = server_socket.accept()
        while True:
            with parser.OsefStream(file_path) as osef_stream:
                _stream_on_socket(osef_stream, client_socket)
                if not repeat:
                    break


def _stream_on_socket(
    osef_stream: parser.OsefStream, connected_socket: socket.SocketType
):
    """Send an osef stream frames to an opened TCP socket at the right frequency"""
    iterator = parser.get_tlv_iterator(osef_stream)
    previous_timestamp = None
    parsing_start_time = time.time()
    for index, tlv in iterator:
        raw_tree = build_tree(tlv)
        if not raw_tree:
            continue

        frame_dict = parse_to_dict(raw_tree)
        timestamp = frame_dict["timestamped_data"]["timestamp_microsecond"]
        packet = struct.pack(
            parser._STRUCT_FORMAT % tlv.length,
            tlv.type,
            tlv.length,
            tlv.value,
        )
        if previous_timestamp is None:
            previous_timestamp = timestamp
        parsing_duration = time.time() - parsing_start_time
        time.sleep(max(timestamp - previous_timestamp - parsing_duration, 0))
        try:
            connected_socket.send(packet)
        except ConnectionResetError:
            break
        parsing_start_time = time.time()
        previous_timestamp = timestamp
