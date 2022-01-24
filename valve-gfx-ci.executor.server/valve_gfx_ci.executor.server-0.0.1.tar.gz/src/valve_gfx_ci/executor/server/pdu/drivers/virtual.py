from .. import logger, PDU, PDUPort, PDUState

import time
import socket
from contextlib import contextmanager


class VirtualPDU(PDU):  # pragma: nocover
    def __init__(self, name, config):
        logger.info("Creating a virtual PDU named %s", name)
        self.host, self.port = config.get('hostname', 'localhost:9191').split(':')
        self.port = int(self.port)
        logger.info("Connecting to %s:%d", self.host, self.port)
        with self.conn() as s:
            s.sendall((0).to_bytes(4, byteorder='big'))
            num_ports = int(s.recv(1)[0])
            self._ports = [PDUPort(self, i) for i in range(num_ports)]
        super().__init__(name)

    @property
    def ports(self):
        return self._ports

    @contextmanager
    def conn(self, *args, **kw):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.connect((self.host, self.port))
        try:
            yield s
        finally:
            s.close()

    def set_port_state(self, port_id, state):
        if state == PDUState.OFF or state == PDUState.REBOOT:
            cmd = (port_id << 2) | 0x02
            with self.conn() as s:
                s.sendall(cmd.to_bytes(4, byteorder='big'))
                assert(s.recv(1)[0] == 0x01)
        if self.state_transition_delay_seconds:
            time.sleep(self.state_transition_delay_seconds)
        if state == PDUState.ON or state == PDUState.REBOOT:
            cmd = (port_id << 2) | 0x01
            with self.conn() as s:
                s.sendall(cmd.to_bytes(4, byteorder='big'))
                assert(s.recv(1)[0] == 0x01)
        if self.state_transition_delay_seconds:
            time.sleep(self.state_transition_delay_seconds)

    def get_port_state(self, port_id):
        cmd = port_id << 2 | 0x03
        with self.conn() as s:
            s.sendall(cmd.to_bytes(4, byteorder='big'))
            state = int(s.recv(1)[0])
            logger.info("port state %x", state)
            if state == 0x03:
                return PDUState.ON
            elif state == 0x04:
                return PDUState.OFF
            elif state == 0x05:
                return PDUState.UNKNOWN
            else:
                assert(False)
