from ..answer.user_action_type import UserActionType


class UserAction:
    """This class will be updated in next versions."""

    def __init__(self, prp_id: int, action: 'UserActionType', prp_value_id: int, value_id: int, value: any, datatype: str,
                 multi: bool, part: int):
        self.prp_id = prp_id
        self.action = action
        self.prp_value_id = prp_value_id
        self.value_id = value_id
        self.value = value
        self.part = part
        self.datatype = datatype
        self.multi = multi

    def as_tuple(self) -> tuple:
        return (self.prp_id, self.action.name, self.prp_value_id, self.value_id,
                self.value, self.part, self.datatype, self.multi)

    def as_dict(self) -> dict:
        return {
            "prp_id": self.prp_id,
            "action": self.action.name,
            "prp_value_id": self.prp_value_id,
            "value_id": self.value_id,
            "value": self.value,
            "part": self.part,
            "datatype": self.datatype,
            "multi": self.multi
        }

    def __str__(self) -> str:
        return str(self.as_tuple())

    def __repr__(self) -> str:
        return str(self.as_dict())
