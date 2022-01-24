from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_MaintenanceFrequencyCode(Codelist):
    pass


@dataclass
class MD_MaintenanceInformation:
    maintenanceAndUpdateFrequency: Optional[
        Codelist[mmi.MD_MaintenanceFrequencyCode]
    ] = None
    maintenanceDate: Optional[list[cit.CI_Date]] = field(default_factory=list)
    userDefinedMaintenanceFrequency: Optional[gco.TM_PeriodDuration] = None
    maintenanceScope: Optional[list[mcc.MD_Scope]] = field(
        default_factory=list
    )
    maintenanceNote: Optional[list[gco.CharacterString]] = field(
        default_factory=list
    )
    contact: Optional[list[cit.CI_Responsibility]] = field(
        default_factory=list
    )
