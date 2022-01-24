from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class SV_CoupledResource:
    ...


@dataclass
class SV_OperationMetadata:
    ...


@dataclass
class SV_OperationChainMetadata:
    ...


@dataclass
class SV_CouplingType(Codelist):
    pass


from .mcc import Abstract_ResourceDescription


@dataclass
class SV_ServiceIdentification(Abstract_ResourceDescription):
    serviceType: Optional[str] = None
    serviceTypeVersion: list[str] = field(default_factory=list)
    accessProperties: Optional[mrd.MD_StandardOrderProcess] = None
    couplingType: Optional[Codelist[srv.SV_CouplingType]] = None
    coupledResource: list[SV_CoupledResource] = field(default_factory=list)
    operatedDataset: list[cit.CI_Citation] = field(default_factory=list)
    profile: list[cit.CI_Citation] = field(default_factory=list)
    serviceStandard: list[cit.CI_Citation] = field(default_factory=list)
    containsOperations: list[SV_OperationMetadata] = field(
        default_factory=list
    )
    operatesOn: list[mri.MD_DataIdentification] = field(default_factory=list)
    containsChain: list[SV_OperationChainMetadata] = field(
        default_factory=list
    )
