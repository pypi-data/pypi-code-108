import datetime
import uuid
from dataclasses import dataclass

@dataclass
class AccountCarrierMap:
  account_id: int
  customer_code: str
  carrier_id: uuid.UUID
  status: str
  warmup_email_sent_at: datetime.date