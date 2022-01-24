from datetime import datetime
from typing import Any, ClassVar, List, Optional

try:
    import constants
except ImportError:
    from . import constants

from pydantic import BaseModel


class AttendeeModel(BaseModel):
    first_names: str
    last_name: str
    name_badge: str
    cell: str
    email: str
    dietary: Optional[str]
    disability: Optional[str]
    first_mdc: bool
    mjf_lunch: bool
    lion: bool
    club: str = None
    partner_program: bool = None
    auto_name_badge: bool = False
    full_name: Optional[str]

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.full_name = f"{self.first_names} {self.last_name}"
        if not self.name_badge:
            self.name_badge = self.full_name
            self.auto_name_badge = True


class RegistrationItems(BaseModel):
    full: int = 0
    banquet: int = 0
    md_convention: int = 0
    theme: int = 0
    pins: int = 0


class Registration(BaseModel):
    reg_num: Optional[int]
    attendees: List[AttendeeModel]
    items: RegistrationItems
    timestamp: datetime
    cost: float = 0
    emails: Optional[list]
    names: Optional[str]
    reg_num_string: Optional[str]

    def __init__(self, **data: Any):
        super().__init__(**data)
        for field in ("full", "banquet", "md_convention", "theme", "pins"):
            self.cost += getattr(constants, f"COST_{field.upper()}", 0) * getattr(
                self.items, field, 0
            )
        self.emails = list(set([attendee.email for attendee in self.attendees]))
        if not self.emails:
            self.emails = None
        self.names = " and ".join([attendee.full_name for attendee in self.attendees])
        self.reg_num_string = f"MDC{self.reg_num:03}"
