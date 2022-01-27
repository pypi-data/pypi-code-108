from enum import Enum
from pydantic import BaseModel, Field


class HeartbeatEventType(str, Enum):
    NEW = 'NEW'
    LOST = 'LOST'


class HeartbeatEvent(BaseModel):
    event_type: HeartbeatEventType = Field(HeartbeatEventType.NEW)
    namespace: str = Field("namespace")
    service_name: str = Field("service_name")
    host_ip: str = Field("0.0.0.0")
    host_name: str = Field("host_name")
    timestamp: int = Field(0)
