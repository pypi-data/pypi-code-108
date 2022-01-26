import json
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, bytes):
            return obj.hex()
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)


def complex_serializer_json_dumps(data: Any) -> str:
    return ComplexEncoder().encode(data)
