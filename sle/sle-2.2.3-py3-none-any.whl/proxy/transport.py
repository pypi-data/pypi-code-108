import queue
import socket
import select
import struct
import time
import errno
import threading

from sle import logger


TML_SLE_FORMAT = '!ii'
TML_SLE_TYPE = 0x01000000
TML_CONTEXT_MSG_FORMAT = '!IIbbbbIHH'
TML_CONTEXT_MSG_TYPE = 0x02000000
TML_HEARTBEAT_FORMAT = '!ii'
TML_HEARTBEAT_TYPE = 0x03000000


class DiagnosticCode:
    TML_PROTOCOL_ERROR = 128
    TML_BAD_FORMAT = 129
    TML_HB_PARAM_NOT_ACCEPTABLE = 130
    TML_ASSOCIATION_ESTAB_TIMEOUT = 131
    TML_HBR_TIMEOUT = 132
    TML_UNEXPECTED_DISCONNECT_BY_PEER = 133
    TML_PREMATURE_DISCONNECT_DURING_PEER_ABORT = 134
    TML_OTHER_REASON = 199


class Role:
    INITIATOR = 'initiator'
    RESPONDER = 'responder'


class State:
    TML_CLOSED = 'closed'
    TML_STARTING = 'starting'
    TML_DATA_TRANSFER = 'data transfer'
    TML_PEER_ABORTING = 'peer aborting'
    TML_CLOSING = 'closing'


class Event:
    HL_CONNECT_REQ = 'hl connect request'
    TCP_CONNECT_CONF = 'tcp connect cnf'
    TCP_CONNECT_IND = 'tcp connect ind'
    TCP_DATA_IND = 'tcp data ind'
    HL_DISCONNECT_REQ = 'hl disconnect req'
    TCP_DISCONNECT_IND = 'tcp disconnect ind'
    DEL_SLE_PDU_REQ = 'del sle pdu req'
    HL_PEER_ABORT_REQ = 'hl peer abort req'
    TCP_URGENT_DATA_IND = 'tcp urgent data ind'
    HL_RESET_REQ = 'hl reset req'
    TCP_ABORT_IND = 'tcp abort ind'
    TCP_TIMEOUT = 'tcp timeout'
    TCP_ERROR = 'tcp error'
    TMS_TIMEOUT = 'tms timeout'
    HBT_TIMEOUT = 'hbt timeout'
    HBR_TIMEOUT = 'hbr timeout'
    CPA_TIMEOUT = 'cpa timeout'


TMS_TIMEOUT = 5  # TML start up timeout
CPA_TIMEOUT = 5  # Close after peer abort timeout


class Timer:

    def __init__(self, parent, timeout, raise_event):
        self._parent = parent
        self._timeout = timeout
        self._raise_event = raise_event
        self._timer = None

    def start(self):
        if self._timer:
            self._timer.cancel()
        if self._timeout > 0:
            self._timer = threading.Timer(self._timeout, self._expired)
            self._timer.start()

    def stop(self):
        if self._timer:
            self._timer.cancel()

    def _expired(self):
        self._parent._trigger_event(self._raise_event)


class TransportMappingLayer:

    def __init__(
            self, proxy, heartbeat, deadfactor,
            buffer_size, role=Role.INITIATOR):
        self._proxy = proxy
        self._heartbeat = heartbeat
        self._deadfactor = deadfactor
        self._buffer_size = buffer_size
        self._role = role

        self._state = State.TML_CLOSED
        self._socket = None
        self._local_peer_abort = False
        self._first_pdu = True
        self.socket_error = False

        hbt_timeout = self._heartbeat
        hbr_timeout = self._heartbeat * self._deadfactor

        self._tms_timer = Timer(self, TMS_TIMEOUT, Event.TMS_TIMEOUT)
        self._hbt_timer = Timer(self, hbt_timeout, Event.HBT_TIMEOUT)
        self._hbr_timer = Timer(self, hbr_timeout, Event.HBR_TIMEOUT)
        self._cpa_timer = Timer(self, CPA_TIMEOUT, Event.CPA_TIMEOUT)

        self._event_queue = queue.Queue()
        self._event_thread = threading.Thread(target=self._event_handler)
        self._event_thread.kill = False

        self._message_thread = threading.Thread(target=self._message_handler)
        self._message_thread.kill = False

    def _event_handler(self):
        thread = threading.currentThread()
        while not thread.kill:
            try:
                event, data = self._event_queue.get(timeout=1)
                self._process_event(event, data)
            except queue.Empty:
                pass

    def _message_handler(self):
        thread = threading.currentThread()

        # wait for the establishment of tcp connection
        while self._socket is None and not thread.kill:
            time.sleep(0.01)

        buffer = bytearray()

        while not thread.kill:
            try:
                readable, _, _ = select.select([self._socket], [], [], 1)
            except Exception:
                pass

            for sock in readable:
                try:
                    buffer += self._socket.recv(self._buffer_size)

                    msg_type = int.from_bytes(buffer[:4], byteorder='big')
                    if msg_type not in [
                        TML_SLE_TYPE,
                        TML_CONTEXT_MSG_TYPE,
                        TML_HEARTBEAT_TYPE
                            ]:
                        # triggers an peer abort due to bad message format
                        data = buffer.copy()  # copy data
                        self._tcp_data_indication(data)
                        buffer = bytearray()  # clear buffer
                    else:
                        pdu_len = int.from_bytes(buffer[4:8], byteorder='big')
                        pdu = buffer[8:]
                        # only when entire pdu was received
                        if len(pdu) >= pdu_len:
                            data = buffer[:8+pdu_len]
                            self._tcp_data_indication(data)
                            buffer = buffer[8+pdu_len:]  # remove from buffer

                except Exception:
                    pass

    def _trigger_event(self, event, data=None):
        self._event_queue.put((event, data))

    def _process_event(self, event, data=None):

        if self._state == State.TML_CLOSED:

            if event == Event.HL_CONNECT_REQ:

                if self._role == Role.INITIATOR:
                    foreign_ip, foreign_port = data
                    self._tcp_connect_request(foreign_ip, foreign_port)
                    self._state = State.TML_STARTING

            elif event == Event.TCP_CONNECT_IND:

                if self._role == Role.RESPONDER:
                    self._start_tms_timer()
                    self._first_pdu = False
                    self._state = State.TML_STARTING

        elif self._state == State.TML_STARTING:

            if event == Event.TCP_CONNECT_CONF:

                if self._role == Role.INITIATOR:
                    # issue TML connect confirmation
                    context_msg = struct.pack(
                        TML_CONTEXT_MSG_FORMAT,
                        TML_CONTEXT_MSG_TYPE,
                        0x0000000C,
                        ord('I'), ord('S'), ord('P'), ord('1'),
                        0x00000001,
                        self._heartbeat,
                        self._deadfactor
                    )
                    self._tcp_data_request(context_msg)
                    self._start_hbr_timer()
                    self._start_hbt_timer()
                    self.connect_confirmation()
                    self._proxy.connected = True
                    self._state = State.TML_DATA_TRANSFER

            elif event == Event.TCP_DATA_IND:

                if self._role == Role.INITIATOR:
                    self._tcp_abort_request()
                    self.protocol_abort_indication()
                    self._state = State.TML_CLOSED
                else:
                    # TODO...
                    raise NotImplementedError

            elif event == Event.TCP_DISCONNECT_IND:

                if self._role == Role.RESPONDER:
                    self._tcp_disconnect_request()
                    self._stop_tms_timer()
                    self._state = State.TML_CLOSED

            elif event == Event.TCP_URGENT_DATA_IND:

                if self._role == Role.RESPONDER:
                    self._tcp_abort_request()
                    self._stop_tms_timer()
                    self._state = State.TML_CLOSED

            elif event == Event.HL_RESET_REQ:

                if self._role == Role.INITIATOR:
                    self._tcp_abort_request()
                    self._state = State.TML_CLOSED

            elif event == Event.TCP_ABORT_IND:

                if self._role == Role.INITIATOR:
                    self.protocol_abort_indication()
                self._state = State.TML_CLOSED

            elif event == Event.TCP_TIMEOUT:

                if self._role == Role.INITIATOR:
                    self._tcp_abort_request()
                    self.protocol_abort_indication()
                    self._state = State.TML_CLOSED

            elif event == Event.TCP_ERROR:

                if self._role == Role.INITIATOR:
                    self.protocol_abort_indication(bytes([
                        DiagnosticCode.TML_ASSOCIATION_ESTAB_TIMEOUT]))

                elif self._role == Role.RESPONDER:
                    self._stop_tms_timer()
                    self._state = State.TML_CLOSED

                self._state == State.TML_CLOSED

            elif event == Event.TMS_TIMEOUT:

                if self._role == Role.RESPONDER:
                    self._tcp_abort_request()
                    self._state == State.TML_CLOSED

        elif self._state == State.TML_DATA_TRANSFER:

            if event == Event.TCP_DATA_IND:

                msg_type = int.from_bytes(data[0:4], byteorder='big')

                if msg_type == TML_SLE_TYPE:

                    if self._role == Role.RESPONDER:
                        if not self._first_pdu:
                            self._restart_hbr_timer()
                        else:
                            self._stop_tms_timer()
                            self._start_hbr_timer()
                            self._first_pdu = False

                    elif self._role == Role.INITIATOR:
                        self._restart_hbr_timer()
                        # extract pdu
                        _, pdu = data[:8], data[8:]
                        self._sle_pdu_indication(pdu)

                elif msg_type == TML_HEARTBEAT_TYPE:

                    self._restart_hbr_timer()

                elif msg_type == TML_CONTEXT_MSG_TYPE:

                    if self._role == Role.RESPONDER and self._first_pdu:
                        self._stop_tms_timer()
                        self.protocol_abort_indication()
                    self._peer_abort(
                        bytes([DiagnosticCode.TML_PROTOCOL_ERROR]))
                    self._state = State.TML_CLOSING

                else:  # no valid TML message
                    self.protocol_abort_indication()
                    if self._role == Role.RESPONDER and self._first_pdu:
                        self._stop_tms_timer()
                    self._peer_abort(bytes([DiagnosticCode.TML_BAD_FORMAT]))
                    self._state = State.TML_CLOSING

            elif event == Event.HL_DISCONNECT_REQ:

                if self._role == Role.INITIATOR:
                    self._tcp_disconnect_request()
                    self._cleanup()
                    self._state = State.TML_CLOSED

                elif self._role == Role.RESPONDER:
                    self._local_peer_abort = False
                    self._stop_hbt_timer()
                    self._restart_hbr_timer()
                    self._state = State.TML_CLOSING

            elif event == Event.TCP_DISCONNECT_IND:

                self._tcp_disconnect_request()
                self.protocol_abort_indication()
                self._cleanup()
                self._state = State.TML_CLOSED

            elif event == Event.DEL_SLE_PDU_REQ:

                # build TML message
                msg = struct.pack(
                    TML_SLE_FORMAT,
                    TML_SLE_TYPE,
                    len(data),
                    ) + data
                self._tcp_data_request(msg)
                self._restart_hbt_timer()

            elif event == Event.HL_PEER_ABORT_REQ:

                self._peer_abort(data)
                self._state = State.TML_CLOSING

            elif event == Event.TCP_URGENT_DATA_IND:

                self._local_peer_abort = False
                self._state = State.TML_PEER_ABORTING

            elif event == Event.HL_RESET_REQ:

                self._tcp_abort_request()
                self._cleanup()
                self._state = State.TML_CLOSED

            elif event == Event.TCP_ABORT_IND:

                self.protocol_abort_indication()
                self._cleanup()
                self._state = State.TML_CLOSED

            elif event == Event.TCP_TIMEOUT:

                self._tcp_abort_request()
                self.protocol_abort_indication()
                self._cleanup()
                self._state = State.TML_CLOSED

            elif event == Event.TCP_ERROR:

                self.protocol_abort_indication()
                self._cleanup()
                self._state = State.TML_CLOSED

            elif event == Event.TMS_TIMEOUT:

                if self._role == Role.RESPONDER:
                    self._tcp_abort_request()
                    self.protocol_abort_indication()
                    self._state = State.TML_CLOSED

            elif event == Event.HBT_TIMEOUT:

                self._tcp_data_request(
                    struct.pack(TML_HEARTBEAT_FORMAT, TML_HEARTBEAT_TYPE, 0))
                self._start_hbt_timer()

            elif event == Event.HBR_TIMEOUT:

                self._tcp_abort_request()
                self.protocol_abort_indication()
                self._cleanup()
                self._state = State.TML_CLOSED

        elif self._state == State.TML_PEER_ABORTING:

            raise NotImplementedError

        elif self._state == State.TML_CLOSING:

            if event == Event.TCP_DATA_IND:

                if not self._local_peer_abort:
                    self._tcp_abort_request()
                    self._stop_hbr_timer()
                    self._state = State.TML_CLOSED
                else:
                    pass  # discard

            elif event == Event.TCP_DISCONNECT_IND:

                self._tcp_disconnect_request()
                self._stop_hbr_timer()
                self._state = State.TML_CLOSED

            elif event == Event.TCP_URGENT_DATA_IND:

                if not self._local_peer_abort:
                    self._tcp_abort_request()
                    self._stop_hbr_timer()
                    self._state = State.TML_CLOSED
                else:
                    self._state = State.TML_PEER_ABORTING

            elif event == Event.TCP_ABORT_IND:

                self._stop_hbr_timer()
                self._state = State.TML_CLOSED

            elif event == Event.TCP_ERROR:

                self._stop_hbr_timer()
                self._state = State.TML_CLOSED

            elif event == Event.HBR_TIMEOUT:

                self._tcp_abort_request()
                self._state = State.TML_CLOSED

            elif event == Event.CPA_TIMEOUT:

                self._tcp_abort_request()
                self._state = State.TML_CLOSED

    def _cleanup(self):
        self._hbr_timer.stop()
        self._hbt_timer.stop()

    def _stop_hbr_timer(self):
        self._hbr_timer.stop()

    def _start_hbr_timer(self):
        self._hbr_timer.start()

    def _restart_hbr_timer(self):
        self._hbr_timer.stop()
        self._hbr_timer.start()

    def _stop_hbt_timer(self):
        self._hbt_timer.stop()

    def _start_hbt_timer(self):
        self._hbt_timer.start()

    def _restart_hbt_timer(self):
        self._hbt_timer.stop()
        self._hbt_timer.start()

    def _start_tms_timer(self):
        self._tms_timer.start()

    def _stop_tms_timer(self):
        self._tms_timer.stop()

    def _start_cpa_timer(self):
        self._cpa_timer.start()

    def _stop_cpa_timer(self):
        self._cpa_timer.stop()

    def _peer_abort(self, diagnostic):
        self._tcp_urgent_data_request(diagnostic)
        # TODO: discard pending data...
        self._local_peer_abort = True
        self._stop_hbt_timer()
        self._stop_hbr_timer()
        self._start_cpa_timer()

    ###########################################################################
    # Higher Layer
    ###########################################################################

    # requests received from higher layer

    def connect_request(self, responder_host, responder_port):
        self._event_thread.start()
        self._message_thread.start()
        self._trigger_event(
            Event.HL_CONNECT_REQ, (responder_host, responder_port))

    def disconnect_request(self):
        self._trigger_event(Event.HL_DISCONNECT_REQ)

    def peer_abort_request(
            self, diagnostics=bytes([DiagnosticCode.TML_OTHER_REASON])):
        self._trigger_event(Event.HL_PEER_ABORT_REQ, diagnostics)

    def reset_request(self):
        self._trigger_event(Event.HL_RESET_REQ)

    # indications sent to higher layer

    def connect_indication(self):
        pass

    def connect_confirmation(self):
        pass

    def peer_abort_indication(self):
        pass

    def protocol_abort_indication(self, diagnostics=None):
        pass

    ###########################################################################
    # Data Encoding Layer
    ###########################################################################

    # request received from DEL
    def sle_pdu_request(self, encoded_pdu):
        self._trigger_event(Event.DEL_SLE_PDU_REQ, encoded_pdu)

    # indication sent to DEL
    def _sle_pdu_indication(self, pdu):
        self._proxy.encoding.sle_pdu_indication(pdu)

    ###########################################################################
    # TCP Layer
    ###########################################################################

    # events sent to TCP layer

    def _tcp_connect_request(self, foreign_ip, foreign_port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_error = False

        try:
            self._socket.connect((foreign_ip, foreign_port))
            self._tcp_connect_confirmation()
        except socket.error:
            logger.error('Socket connection failure')
            self.socket_error = True
            self._tcp_error()

    def _tcp_disconnect_request(self):
        self._message_thread.kill = True
        self._event_thread.kill = True
        self._proxy.connected = False
        self._socket.close()
        self._socket = None

    def _tcp_data_request(self, data):
        try:
            self._socket.send(data)
        except socket.error as e:
            if e.errno == errno.ECONNRESET:
                logger.error('Socket connection lost')
                self.socket_error = True
                self._tcp_error()
            elif isinstance(e, BrokenPipeError):
                logger.error('Connection error')
                return
            else:
                logger.error(
                    'Unexpected error encountered when sending data...')
            raise e

    def _tcp_urgent_data_request(self, data):
        # TODO: set urgent flag in TCP frame
        self._tcp_data_request(data)

    def _tcp_abort_request(self):
        self._tcp_disconnect_request()

    # events received from TCP layer

    def _tcp_connect_indication(self):
        self._trigger_event(Event.TCP_CONNECT_IND)

    def _tcp_connect_confirmation(self):
        self._trigger_event(Event.TCP_CONNECT_CONF)

    def _tcp_disconnect_indication(self):
        self._trigger_event(Event.TCP_DISCONNECT_IND)

    def _tcp_data_indication(self, msg):
        self._trigger_event(Event.TCP_DATA_IND, msg)

    def _tcp_urgent_data_indication(self):
        self._trigger_event(Event.TCP_URGENT_DATA_IND)

    def _tcp_abort_indication(self):
        self._trigger_event(Event.TCP_ABORT_IND)

    def _tcp_error(self):
        self._trigger_event(Event.TCP_ERROR)

    def _tcp_timeout(self):
        self._trigger_event(Event.TCP_TIMEOUT)
