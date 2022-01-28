from .. import http_protocol
from .. import protocol


SERVER_VERSION = http_protocol.ServerVersion(
    protocol_version=protocol.VERSION,
    server_type="hashback",
    server_version="1.0",
    server_authors=["Philip Couling"],
)
