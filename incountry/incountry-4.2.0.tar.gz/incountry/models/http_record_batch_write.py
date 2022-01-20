from typing import List, Union, Any

from pydantic import BaseModel

from .record_from_server import RecordFromServer


class RecordsList(BaseModel):
    records: List[RecordFromServer]


class HttpRecordBatchWrite(BaseModel):
    body: Union[RecordsList, Any]
