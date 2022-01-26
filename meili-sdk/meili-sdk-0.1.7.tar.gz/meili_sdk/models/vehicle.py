import typing as t

from meili_sdk.exceptions import ValidationError
from meili_sdk.models.base import BaseModel


class Vehicle(BaseModel):
    uuid: t.Optional[str] = None
    external_identifier: t.Optional[str] = None
    verbose_name: t.Optional[str] = None
    slug: t.Optional[str] = None
    vehicle_type: t.Optional[str] = None
    active: bool = True
    category: t.Optional[str] = None
    team: t.Optional[str] = None
    emergency_battery_level: t.Optional[float] = None
    emergency_distance: t.Optional[float] = None
    use_team_battery_defaults: bool = True
    manufacturer: t.Optional[str] = None

    def validate_vehicle_type(self):
        if self.vehicle_type not in ["inside", "outside"]:
            raise ValidationError(f"Invalid vehicle type: {self.vehicle_type}")
        return self.vehicle_type
