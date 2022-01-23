# -*- coding: utf-8 -*-
"""Module containing the class implementing the record layer
"""
# import basic stuff
import logging
from typing import Any, Optional

# import own stuff
import tlsmate.config as conf
import tlsmate.pdu as pdu
import tlsmate.record_layer_state as record_layer_state
import tlsmate.recorder as rec
import tlsmate.socket as socket
import tlsmate.structs as structs
import tlsmate.tls as tls

# import other stuff


class RecordLayer(object):
    """Class implementing the record layer.
    """

    def __init__(self, config: conf.Configuration, recorder: rec.Recorder) -> None:
        self._send_buffer = bytearray()
        self._receive_buffer = bytearray()
        self._fragment_max_size = 4 * 4096
        self._write_state: Optional[record_layer_state.RecordLayerState] = None
        self._read_state: Optional[record_layer_state.RecordLayerState] = None
        self._socket = socket.Socket(config=config, recorder=recorder)
        self._flush_each_fragment = False
        self._ssl2 = False

    def _send_fragment(self, rl_msg: structs.RecordLayerMsg, **kwargs: Any) -> None:
        """Protects a fragment and adds it to the send queue.

        Arguments:
            rl_msg: The record layer message to be sent.
        """

        if self._write_state is not None:
            rl_msg = self._write_state.protect_msg(rl_msg, **kwargs)

        self._send_buffer.extend(pdu.pack_uint8(rl_msg.content_type.value))
        self._send_buffer.extend(pdu.pack_uint16(rl_msg.version.value))
        self._send_buffer.extend(pdu.pack_uint16(len(rl_msg.fragment)))
        self._send_buffer.extend(rl_msg.fragment)
        if self._flush_each_fragment:
            self.flush()

    def _fragment(self, rl_msg, **kwargs):
        """Fragments a given message according the maximum fragment size.

        Each fragment is then protected (if applicable) and added to the send queue.

        Arguments:
            rl_msg (:obj:`tlsmate.structs.RecordLayerMsg`): The message to be sent.
        """
        if rl_msg is None or len(rl_msg.fragment) <= self._fragment_max_size:
            self._send_fragment(rl_msg, **kwargs)
            return

        message = rl_msg.fragment
        while len(message) > self._fragment_max_size:
            frag = message[: self._fragment_max_size]
            message = message[self._fragment_max_size :]
            self._send_fragment(
                structs.RecordLayerMsg(
                    content_type=rl_msg.content_type,
                    version=rl_msg.version,
                    fragment=frag,
                )
            )

        if len(message):
            self._send_fragment(
                structs.RecordLayerMsg(
                    content_type=rl_msg.content_type,
                    version=rl_msg.version,
                    fragment=message,
                )
            )

    def send_message(self, message: structs.RecordLayerMsg, **kwargs: Any) -> None:
        """Does everything the record layer needs to do for sending a message.

        The message is fragmented and protected (i.e. encrypted and authenticated) if
        applicable. Compression is not supported.

        Minimal support for SSL2 is provided as well (no fragmentation, no protection).

        The message may result in multiple fragments to be sent. The fragments are
        added to the send queue but actually not sent to the network yet. Use the
        flush method to do so.

        Arguments:
            message: The message to send.
        """

        if message and message.content_type is tls.ContentType.SSL2:
            self._ssl2 = True
            self._send_buffer.extend(pdu.pack_uint16(len(message.fragment) | 0x8000))
            self._send_buffer.extend(message.fragment)

        else:
            self._fragment(message, **kwargs)

    def open_socket(self, l4_addr: structs.TransportEndpoint) -> None:
        """Opens the socket

        Arguments:
            l4_addr : the l4_addr
        """

        self._socket.open_socket(l4_addr)

    def close_socket(self) -> None:
        """Closes the socket. Obviously.
        """

        self._socket.close_socket()

    def flush(self) -> None:
        """Send all fragments in the send queue.

        This function is useful if e.g. multiple handshake messages shall be sent
        in one record layer message.
        """

        self._socket.sendall(self._send_buffer)
        self._send_buffer = bytearray()

    def wait_rl_msg(
        self, timeout: int = 5, **kwargs: Any
    ) -> Optional[structs.RecordLayerMsg]:
        """Wait for a record layer message to be received from the network.

        Arguments:
            timeout: The timeout in seconds to wait for the message. This
                parameter is optional and defaults to 5 seconds.

        Returns:
            A complete record layer message. If a timeout occurs, None is returned.

        Raises:
            ServerMalfunction: If anything went wrong, e.g. message could not be
                authenticated, wrong padding, etc.
        """

        # wait for record layer header
        rl_len = 2 if self._ssl2 else 5
        while len(self._receive_buffer) < rl_len:
            data = self._socket.recv_data(timeout=timeout)
            if data is None or not len(data):
                # TODO: timeout
                return None

            self._receive_buffer.extend(data)

        if self._ssl2:
            content_type = tls.ContentType.SSL2
            version = tls.Version.SSL20
            length, offset = pdu.unpack_uint16(self._receive_buffer, 0)
            if (length & 0x8000) == 0:
                length &= 0x3FFF  # don't evaluate is-escape bit
                offset += 1  # skip padding byte
                rl_len = 3

            else:
                length &= 0x7FFF

        else:
            ct_type, offset = pdu.unpack_uint8(  # type: ignore
                self._receive_buffer, 0
            )
            content_type = tls.ContentType.val2enum(ct_type, alert_on_failure=True)
            vers, offset = pdu.unpack_uint16(  # type: ignore
                self._receive_buffer, offset
            )
            version = tls.Version.val2enum(vers, alert_on_failure=True)
            length, offset = pdu.unpack_uint16(self._receive_buffer, offset)

        while len(self._receive_buffer) < (length + rl_len):
            data = self._socket.recv_data(timeout=timeout)
            if data is None or not len(data):
                # TODO: timeout
                return None

            self._receive_buffer.extend(data)

        # here we have received at least a complete record layer fragment
        fragment = bytes(self._receive_buffer[rl_len : (length + rl_len)])
        self._receive_buffer = self._receive_buffer[(length + rl_len) :]

        rl_msg = structs.RecordLayerMsg(
            content_type=content_type, version=version, fragment=fragment
        )

        if self._read_state is None:
            return rl_msg

        else:
            return self._read_state.unprotect_msg(rl_msg, **kwargs)

    def update_state(self, new_state: structs.StateUpdateParams) -> None:
        """Update the record layer state.

        I.e. sent or received fragments are encrypted and authenticated.

        Arguments:
            new_state (:obj:`tlsmate.structs.StateUpdateParams`): A complete
                state (either a read state or a write state), containing the
                keying material for the symmetric ciphers and other relevant elements.
        """

        state = record_layer_state.RecordLayerState(new_state)
        if new_state.is_write_state:
            self._write_state = state
            state_type = "WRITE"

        else:
            self._read_state = state
            state_type = "READ"

        logging.debug(f"switching record layer state: {state_type}")
        logging.debug(f"{state_type} enc key: {pdu.dump(state._keys.enc)}")
        if state._iv:
            logging.debug(f"{state_type} iv: {pdu.dump(state._iv)}")

        if state._keys.mac:
            logging.debug(f"{state_type} hmac key: {pdu.dump(state._keys.mac)}")
