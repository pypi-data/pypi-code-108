from typing import Optional

from pydantic import BaseModel


class FirewallRule(BaseModel):
    name: str
    start_ip_address: str
    end_ip_address: str
    type: Optional[str] = None
