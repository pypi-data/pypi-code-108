from enum import Enum
from datetime import datetime
from typing import List


class TypeEnum(Enum):
    CALL = "call"
    SMS = "sms"


class AlertCOM:
    ID_alert_communication: int
    phone: str
    ID_org: int
    ID_rule: int
    type: TypeEnum
    created_at: datetime
    updated_at: datetime

    def __init__(self, ID_alert_communication: int, phone: str, ID_org: int, ID_rule: int, type: TypeEnum, created_at: datetime, updated_at: datetime) -> None:
        self.ID_alert_communication = ID_alert_communication
        self.phone = phone
        self.ID_org = ID_org
        self.ID_rule = ID_rule
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at


class AlertRuleData:
    data: List[AlertCOM] = []

    def __init__(self, data) -> None:
        self.data = []
        for param in data:
            self.data.append(AlertCOM(**dict(param)))
