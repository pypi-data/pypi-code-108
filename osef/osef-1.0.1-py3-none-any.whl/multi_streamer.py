"""Tools to stream multiple osefs on TCP sockets."""
import ipaddress
import logging
import pathlib
import socket
import struct
import threading
import time
from typing import List

import osef.parser
from osef._logger import osef_logger
from osef.types import OsefTypes


class MultiOsefStreamer:
    """Stream multiple osef files on a TCP socket with the right inter frame
       timing. The different osef are streamed synchronously with a shared clock

    :param osef_list: List of objects containing the osef and network information.

    Example:
    [
        {
            "osef_path": "/data/file.osef",
            "ip": "192.168.2.4",
            "port": 11111
        },
        ...
    ]
    """

    class FirstTimestampError(Exception):
        """Exception raised when first timestamp could not be retrieved."""

        def __init__(self, message):
            super().__init__(f"Could not retrieve first timestamps from {message}")

    def __init__(self, osef_list, should_overwrite=False):
        self.__should_stop = False
        self.__should_stop_mutex = threading.Lock()

        self.__osef_list = osef_list
        self.__first_timestamp = None  # First timestamp of the earliest osef
        self.__delta_clock = None  # Difference between the first_timestamp and now

        self.__number_of_threads = len(self.__osef_list)
        self.__connected_mutex = threading.Lock()
        self.__connected = 0  # Shared variable to know when every thread is ready

        self.__cv = threading.Condition()  # To notify the threads to start
        self.__threads: List[threading.Thread] = []

        self.__timeout = 0.00001  # 10 microseconds

        self.__should_overwrite = should_overwrite

    def __enter__(self):
        """Parse the osef_list to retrieve the earliest timestamp and initialize
        the streaming threads
        """
        osef_logger.info(f"Number of threads: {self.__number_of_threads}")
        for i in range(self.__number_of_threads):
            port = self.__osef_list[i]["port"]
            ip_addr = self.__osef_list[i]["ip"]
            try:
                ip_addr = ipaddress.ip_address(ip_addr)
            except ValueError as value_exception:
                osef_logger.error("Wrong ip address format: '{ip_addr}'")
                raise value_exception
            osef_path = self.__osef_list[i]["osef_path"]
            filepath = pathlib.Path(osef_path)
            if not filepath.is_file():
                raise FileNotFoundError(f"File {osef_path} could not be found.")

            first_ts = _get_first_timestamp(osef_path)
            if first_ts is None:
                raise MultiOsefStreamer.FirstTimestampError(osef_path)
            if self.__first_timestamp is None or first_ts < self.__first_timestamp:
                self.__first_timestamp = first_ts
            osef_logger.info(f"Thread {i} will bind to {ip_addr}:{port}")
            self.__threads.append(
                threading.Thread(
                    target=self.__streamer_thread, args=(osef_path, ip_addr, port, i)
                )
            )

        osef_logger.info(f"First timestamp is: {self.__first_timestamp}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for thread in self.__threads:
            thread.join()

    def __del__(self):
        self.stop()

    def run(self):
        """Start the streaming threads"""
        for thread in self.__threads:
            thread.start()

    def stop(self):
        """Stop streaming thread"""
        with self.__should_stop_mutex:
            self.__should_stop = True

    def __streamer_thread(self, file_path, ip_address, port, thread_id):
        """The streaming threads entry
        Once connected to a client, the thread waits for its threadmates to be
        connected as well. The last one calculates the clock difference between
        now and the first timestamp for synchronization purpose, and then notify
        the others to start.
        """
        osef_logger.info(f"Starting thread [{thread_id}] for osef '{file_path}'")
        server_socket = _create_accepting_socket(ip_address, port)
        client_socket, _ = server_socket.accept()
        client_socket.settimeout(self.__timeout)
        thread_running_number = -1
        with self.__connected_mutex:
            self.__connected += 1
            thread_running_number = self.__connected
            osef_logger.info(f"{self.__connected}: Thread {thread_id} connected!")
        with self.__cv:
            # If last one, calculates delta clock and notify others
            if thread_running_number == self.__number_of_threads:
                # delta_clock and first_timestamp do not need to be protected
                # against shared access since only the last thread should update
                # self.__delta_clock
                # One second is added to let time for other threads to be notified
                self.__delta_clock = time.time() - self.__first_timestamp + 1
                osef_logger.info(
                    f"Thread {thread_id} setting delta to {self.__delta_clock}"
                )
                self.__cv.notifyAll()
            # Not last one: waits for delta clock to be set
            else:
                while self.__delta_clock is None:
                    self.__cv.wait()
        with osef.parser.OsefStream(file_path) as osef_stream:
            osef_logger.info(f"Thread {thread_id} Start sending {file_path}")
            self.__stream_on_socket(
                osef_stream, client_socket, server_socket, thread_id
            )

    def __stream_on_socket(
        self,
        osef_stream: osef.parser.OsefStream,
        connected_socket: socket.SocketType,
        server_socket,
        thread_id,
    ):
        """Send an osef stream frames to an opened TCP socket at the right frequency"""
        iterator = osef.parser.get_tlv_iterator(osef_stream)
        for index, tlv in iterator:
            with self.__should_stop_mutex:
                if self.__should_stop is True:
                    osef_logger.info(f"Thread {thread_id} shutting down...")
                    break
            timestamp, ts_index = _get_timestamp_from_tlv_bytes(tlv.value, tlv.length)
            should_run_timestamp = timestamp + self.__delta_clock
            packet = struct.pack(
                osef.parser._STRUCT_FORMAT % tlv.length,
                tlv.type,
                tlv.length,
                _overwrite_timestamp(
                    should_run_timestamp, bytearray(tlv.value), ts_index
                )
                if self.__should_overwrite
                else tlv.value,
            )
            sleep_time = should_run_timestamp - time.time()
            if sleep_time > 0.0001:
                time.sleep(sleep_time)
            try:
                connected_socket.send(packet)
            except (socket.timeout, TimeoutError):
                osef_logger.warning("Client too slow, moving on to the next packet")
            except ConnectionResetError as connection_reset_except:
                logging.warning(
                    f"Connection closed unexpectedly \
                    ({connection_reset_except}), reaccepting..."
                )
                connected_socket, _ = server_socket.accept()
                connected_socket.settimeout(self.__timeout)
                logging.info(f"Thread {thread_id} reconnected!")


def _overwrite_timestamp(new_timestamp, tlv_bytesarray, ts_index):
    tlv_bytesarray[ts_index : ts_index + 4] = int(new_timestamp).to_bytes(4, "little")
    tlv_bytesarray[ts_index + 4 : ts_index + 8] = int(
        (new_timestamp * 1000000) % 1000000
    ).to_bytes(4, "little")
    return bytes(tlv_bytesarray)


def _get_timestamp_from_tlv_bytes(tlv_bytes, tlv_length):
    """Parse the tlv binary data looking for the timestamp

    :return success: timestamp stored in the tlv packet in seconds
    :return failure: -1
    """
    current = 0
    osef_type = int.from_bytes(tlv_bytes[current : current + 4], byteorder="little")
    current += 4
    length = int.from_bytes(tlv_bytes[current : current + 4], byteorder="little")
    while osef_type != OsefTypes.TIMESTAMP_MICROSECOND and current < tlv_length:
        current += length
        osef_type = int.from_bytes(tlv_bytes[current : current + 4], byteorder="little")
        current += 4
        length = int.from_bytes(tlv_bytes[current : current + 4], byteorder="little")
    if osef_type == OsefTypes.TIMESTAMP_MICROSECOND:
        if length != 8:
            logging.error("Error: timestamp length should be 8")
            return -1
        current += 4
        seconds = int.from_bytes(tlv_bytes[current : current + 4], byteorder="little")
        microseconds = int.from_bytes(
            tlv_bytes[current + 4 : current + 8], byteorder="little"
        )
        timestamp = seconds + microseconds / 1000000
        return timestamp, current
    return -1, -1


def _get_first_timestamp(file_path):
    """Retrieve the first timestamp of an osef file

    :return success: timestamp stored in the tlv packet in seconds
    :return failure: -1
    """
    timestamp = None
    try:
        with osef.parser.OsefStream(file_path) as osef_stream:
            tlv = osef.parser.read_next_tlv(osef_stream)
            while tlv and timestamp is None:
                timestamp, _ = _get_timestamp_from_tlv_bytes(tlv.value, tlv.length)
                tlv = osef.parser.read_next_tlv(osef_stream)
    except EOFError:
        pass
    return timestamp


def _create_accepting_socket(ip_address, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # to avoid: [Errno 98] Address already in use.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # connect socket to client
    server_socket.bind((format(ip_address), port))
    server_socket.listen(1)
    return server_socket
