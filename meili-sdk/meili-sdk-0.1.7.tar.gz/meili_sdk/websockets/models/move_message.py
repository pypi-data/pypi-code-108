from meili_sdk.models.base import BaseModel

__all__ = ("MoveMessage",)


class MoveMessage(BaseModel):
    type: str
    location: dict

    @property
    def is_charge(self):
        return self.type == "move_charge"

    @property
    def is_inside(self):
        return "x" in self.location

    @property
    def is_outdoor(self):
        return not self.is_inside
