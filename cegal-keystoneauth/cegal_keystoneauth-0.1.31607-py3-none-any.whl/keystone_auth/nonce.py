# Copyright 2021 Cegal AS
# All rights reserved

from datetime import datetime, timedelta
from secrets import token_urlsafe


class _Nonce:
    def __init__(self) -> None:
        self.nonce = token_urlsafe(43)
        self.expires = datetime.utcnow() + timedelta(minutes=10)

    def has_expired(self):
        return self.expires <= datetime.utcnow()
