"""
Module containing handlers for Zabbix protocol.
"""

from ast import Return
from typing import Optional, Dict
import abc
import socket
import struct
import logging
import json
from enum import Flag, IntEnum
from OpenSSL.SSL import Context, Connection, TLSv1_2_METHOD
from openssl_psk import patch_context


logger = logging.getLogger(__name__)


ZBX_HEADER_LEN = 13


class ProtocolFlags(Flag):
    ZABBIX = b'\x01'
    COMPRESSION = b"\x02"
    LARGE_PACKET = b"\x04"


class PSKEnum(IntEnum):
    IDENTITY_MIN_LENGTH = 1
    IDENTITY_MAX_LENGTH = 128
    PSK_MIN_LENGTH = 32
    PSK_MAX_LENGTH = 512



class _Dstream(abc.ABC):
    def __init__(self, target: str, port: int = 10051, source_address: Optional[str] = None) -> None:
        self._ip = target
        self._port = port
        self._source_address = source_address
        self._psk = b''
        self._psk_identity = b''


    def set_psk_encryption(self, identity: str, psk: str):
        if not (PSKEnum.IDENTITY_MIN_LENGTH <= len(identity) <= PSKEnum.IDENTITY_MAX_LENGTH):
            raise ValueError("PSK identity lenght out of bounds")
        if  not (PSKEnum.PSK_MIN_LENGTH <= len(psk) <= PSKEnum.PSK_MAX_LENGTH):
            raise ValueError("PSK key lenght out of bounds")

        patch_context()
        try:
            self._psk  = bytes.fromhex(psk)
            self._psk_identity = identity.encode()
        except ValueError:
            raise ValueError("The provided PSK key is not hexadecimal")


    def _wrap_psk_socket(self, sock):
        def client_callback(conn, identity_hint):
            return (self._psk_identity, self._psk)
        ctx = Context(TLSv1_2_METHOD)
        ctx.set_cipher_list(b'EECDH+aRSA+AES128:RSA+aRSA+AES128:kECDHEPSK+AES128:kPSK+AES128')
        ctx.set_psk_client_callback(client_callback)
        return Connection(ctx, sock)


    def _get_socket(self) -> socket.socket:
        address_family = socket.getaddrinfo(self._ip, self._port)[0][0]
        return socket.socket(address_family)


    def _send(self, payload: bytes) -> str:
        data = b""
        parsed = ""
        s = None
        try:
            s = self._get_socket()
            if self._source_address:
                s.bind((self._source_address, 0))
                logger.info(f"Opening connection to {self._ip}:{self._port} with source address {self._source_address}")
            else:
                logger.info(f"Opening connection to {self._ip}:{self._port}")
            if self._psk and self._psk_identity:
                s = self._wrap_psk_socket(s)
            packed = self._pack_request(payload)
            s.connect((self._ip, self._port))
            s.sendall(packed)
            data = self._recv_response(s)
            parsed = self._unpack_response(data)
        except socket.error:
            logger.exception(f"Cannot connect to host {self._ip}:{self._port}:")
        except struct.error:
            logger.exception("Recived response is corrupted:")
        except Exception:
            logger.exception("Something really bad happened:")
        finally:
            if s is not None:
                logger.info(f"Closing connection to {self._ip}:{self._port}")
                s.close()
            return parsed

    def _unpack_response(self, response: bytes) -> str:
        _, protocol, length, _ = struct.unpack('<4s1sLL', response[:ZBX_HEADER_LEN])
        data = struct.unpack(
            f'<{length}s',
            response[ZBX_HEADER_LEN:ZBX_HEADER_LEN+length]
            )[0]

        return data.decode('utf-8')

    def _pack_request(self, payload: bytes) -> bytes:
        payload_len = len(payload)
        packed = struct.pack(
            f'<4scL4s{payload_len}s',
            b'ZBXD',
            ProtocolFlags.ZABBIX.value,
            payload_len,
            b"\x00\x00\x00\x00",
            payload
            )
        logger.debug(f"Packed payload for {self._ip}:{self._port}. Payload length: {payload_len}. Length with headers: {len(packed)}")
        return packed

    def _recv_response(self, socket_: socket.socket, buff: int = 1024) -> bytes:
        data = b""
        buffer = socket_.recv(buff)
        _, data_length = struct.unpack('<5sQ', buffer[:ZBX_HEADER_LEN])
        logger.debug(f"Received {len(buffer)} from {self._ip}:{self._port}")
        while buffer:
            data += buffer
            if len(data[ZBX_HEADER_LEN:]) < data_length:
                buffer = socket_.recv(buff)
                logger.debug(f"Received {len(buffer)} from {self._ip}:{self._port}")
            else:
                break

        logger.debug(f"Completed data retrieval from {self._ip}:{self._port}. Total length: {len(data)}")
        return data

    @staticmethod
    def _parse_server_response(info) -> Optional[Dict]:
        try:
            response = json.loads(info)
        except json.decoder.JSONDecodeError:
            return None
        data = response.get('info', None)
        splitted = [x.strip().split(':') for x in data.split(';')]
        for i, split in enumerate(splitted):
            name, val = split
            splitted[i][1] = float(val) if name == 'seconds spent' else int(val)
        return dict(splitted)
