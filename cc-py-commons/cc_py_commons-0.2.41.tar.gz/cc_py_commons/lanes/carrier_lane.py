import uuid
import datetime
from dataclasses import dataclass, field

from cc_py_commons.lanes.lane import Lane

@dataclass
class CarrierLane:

  carrierId: uuid.UUID
  laneDTO: Lane
  hasBackhaulLane: bool = field(default=False)
  isBackhaulLane: bool = field(default=False)
  createBackhaulLanes: bool = field(default=False)
  deleted: bool = field(default=False)
  weeklyFrequency: int = field(default=False)
  runDaily: bool = field(default=False)
  monday: bool = field(default=False)
  tuesday: bool = field(default=False)
  wednesday: bool = field(default=False)
  thursday: bool = field(default=False)
  friday: bool = field(default=False)
  saturday: bool = field(default=False)
  sunday: bool = field(default=False)
  age: float = field(default=None)
  rating: int = field(default=False)
  rate: int = field(default=False)
  rateUpdatedAt: datetime.date = field(default=None)
  fromCarrier: bool = field(default=False)
  toBeReviewed: bool = field(default=False)