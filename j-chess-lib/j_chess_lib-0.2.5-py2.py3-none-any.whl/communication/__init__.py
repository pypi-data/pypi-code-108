try:
    from .schema import *
except ImportError as e:
    raise ImportError("Failed to import communication classes provided by schema. Did you install them?") from e

from .connection.Connection import Connection
schema_version = JchessMessage.schema_version

__all__ = [
    "Connection",
    "JchessMessage", "JchessMessageType", "schema_version", "MoveData", "MatchStatusData", "MatchFormatData"
]
