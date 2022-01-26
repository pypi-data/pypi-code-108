from typing import Optional, Dict

from datetime import datetime

from pydantic import BaseModel
from eyja.utils import now

from eyja_influxdb import InfluxDBHub


class TimePoint(BaseModel):
    time: Optional[datetime] = now()
    measurement: str
    tags: Dict[str, str]
    fields: Dict[str, float]

    async def send(self):
        await InfluxDBHub.send(self.dict())
