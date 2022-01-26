from .authentication import AuthenticationLayer
from .encoding import DataEncodingLayer
from .transport import TransportMappingLayer


class Proxy:

    def __init__(
            self,
            service_layer,
            local_identifier, peer_identifier,
            local_password, peer_password,
            auth_level,
            asn1spec,
            heartbeat, deadfactor, buffer_size):
        self.connected = False

        self.service_layer = service_layer
        self.authentication = AuthenticationLayer(
            self, local_identifier, peer_identifier, local_password,
            peer_password, auth_level)
        self.encoding = DataEncodingLayer(self, asn1spec)
        self.transport = TransportMappingLayer(
            self, heartbeat, deadfactor, buffer_size)
