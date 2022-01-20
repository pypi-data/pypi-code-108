from typing import Union, Any

from pydantic import BaseModel

from .record_from_server import RecordFromServer


class HttpRecordWrite(BaseModel):
    body: Union[RecordFromServer, Any]
