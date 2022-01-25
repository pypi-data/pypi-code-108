from typing import List
from dataclasses import dataclass
from datetime import datetime, timezone

from origin.serialize import Serializable


@dataclass
class InternalToken(Serializable):
    """
    TODO
    """
    issued: datetime
    expires: datetime

    # The user performing action(s)
    actor: str

    # The subject we're working with data on behalf of
    subject: str

    # Scopes granted on subject's data
    # meteringpoints.read, measurements.read, emissions.read, etc
    scope: List[str]

    @property
    def is_valid(self) -> bool:
        """
        A token is valid only if its issued before now, and expires
        after now.
        """
        return self.issued <= datetime.now(tz=timezone.utc) < self.expires
