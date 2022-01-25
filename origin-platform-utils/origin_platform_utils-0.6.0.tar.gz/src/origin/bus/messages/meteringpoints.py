from dataclasses import dataclass
from typing import Dict, Any, Optional

from origin.bus import Message
from origin.models.common import Address
from origin.models.tech import TechnologyCodes
from origin.models.meteringpoints import MeteringPoint


@dataclass
class MeteringPointUpdate(Message):
    """
    Event.

    A MeteringPoint has either been added to the system,
    or an existing MeteringPoint has had its details updated.
    """
    meteringpoint: MeteringPoint


@dataclass
class MeteringPointRemoved(Message):
    """
    Event.

    A MeteringPoint has been remove from the system.
    # TODO Advice to perform Clean-up?
    """
    gsrn: str


@dataclass
class MeteringPointTechnologyUpdate(Message):
    """
    Event.

    Updates technology codes for a MeteringPoint.

    Providing None value for 'codes' indicates that services should
    reset/forget existing technology codes.
    """
    gsrn: str
    codes: Optional[TechnologyCodes]


@dataclass
class MeteringPointAddressUpdate(Message):
    """
    Event.

    Updates address for a MeteringPoint.

    Providing None value for 'address' indicates that services should
    reset/forget existing address.
    """
    gsrn: str
    address: Optional[Address]


@dataclass
class ImportMeteringPoints(Message):
    """
    Command.

    Request system to import a MeteringPoint.

    TODO Describe more
    """
    subject: str
    params: Dict[str, Any]

    # Pre-defined param keys:
    GSRN = 'GSRN'
    WEB_ACCESS_CODE = 'WEB_ACCESS_CODE'
    CVR = 'CVR'
    CPR = 'CPR'
