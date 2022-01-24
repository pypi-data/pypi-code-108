from .. import PDU, PDUPort, PDUState


class DummyPDU(PDU):
    def __init__(self, name, config):
        self._ports = []

        for i, port_label in enumerate(config.get('ports', [])):
            port = PDUPort(self, i, port_label)
            port._state = PDUState.ON
            self._ports.append(port)

        super().__init__(name)

    @property
    def ports(self):
        return self._ports

    def set_port_state(self, port_id, state):
        port = self.ports[int(port_id)]
        port._state = state

    def get_port_state(self, port_id):
        port = self.ports[int(port_id)]
        return port._state
