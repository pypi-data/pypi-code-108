import uuid
import datetime
from dataclasses import dataclass, field
from typing import List

@dataclass
class BidHistory:
  id: uuid.UUID
  bid_id: uuid.UUID
  source_type: str
  source_id: int
  amount: int
  carrier_id: uuid.UUID
  pickup_date: datetime.datetime
  delivery_date: datetime.datetime