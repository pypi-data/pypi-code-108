from typing import List

from pydantic import StrictBool, StrictInt

from .record import Record, USER_DATE_KEYS
from .common.custom_types import DatetimeField
from .attachment_meta import AttachmentMeta

SERVER_DATE_KEYS = [
    "created_at",
    "updated_at",
]

ALL_DATE_KEYS = SERVER_DATE_KEYS + USER_DATE_KEYS


class RecordFromServer(Record):
    version: StrictInt = None
    is_encrypted: StrictBool = None
    created_at: DatetimeField = None
    updated_at: DatetimeField = None
    expires_at: DatetimeField = None
    attachments: List[AttachmentMeta] = None
