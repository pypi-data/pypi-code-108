import uuid
from dataclasses import dataclass, field
@dataclass
class Contact:
  email_address: str
  id: uuid.UUID = field(default=None)
  carrier_id: uuid.UUID = field(default=None)
  first_name: str = field(default=None)
  last_name: str = field(default=None)
  phone: str = field(default=None)
  mobile: str = field(default=None)
  primary_contact: bool = field(default=False)
