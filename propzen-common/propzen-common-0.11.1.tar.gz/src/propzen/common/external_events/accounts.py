from uuid import UUID
from dataclasses import dataclass
from propzen.common.service_layer.externalbus import ExternalEvent


@dataclass
class AccountRegistered(ExternalEvent):
    fullname: str
    email: str
    token: str


@dataclass
class AccountConfirmed(ExternalEvent):
    account_id: UUID
    fullname: str
    email: str
