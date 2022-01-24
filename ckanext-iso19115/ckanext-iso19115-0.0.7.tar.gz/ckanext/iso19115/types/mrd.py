from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_MediumFormatCode(Codelist):
    pass


@dataclass
class MD_Distributor:
    distributorContact: cit.CI_Responsibility
    distributionOrderProcess: Optional[
        list[mrd.MD_StandardOrderProcess]
    ] = field(default_factory=list)
    distributorFormat: Optional[list[mrd.MD_Format]] = field(
        default_factory=list
    )
    distributorTransferOptions: Optional[
        list[mrd.MD_DigitalTransferOptions]
    ] = field(default_factory=list)


@dataclass
class MD_DigitalTransferOptions:
    unitsOfDistribution: Optional[gco.CharacterString] = None
    transferSize: Optional[gco.Real] = None
    onLine: Optional[list[cit.CI_OnlineResource]] = field(default_factory=list)
    offLine: Optional[list[mrd.MD_Medium]] = field(default_factory=list)
    transferFrequency: Optional[gco.TM_PeriodDuration] = None
    distributionFormat: Optional[list[mrd.MD_Format]] = field(
        default_factory=list
    )


@dataclass
class MD_Medium:
    name: Optional[cit.CI_Citation] = None
    density: Optional[gco.Real] = None
    densityUnits: Optional[gco.CharacterString] = None
    volumes: Optional[gco.Integer] = None
    mediumFormat: Optional[list[Codelist[mrd.MD_MediumFormatCode]]] = field(
        default_factory=list
    )
    mediumNote: Optional[gco.CharacterString] = None
    identifier: Optional[mcc.MD_Identifier] = None


@dataclass
class MD_Format:
    formatSpecificationCitation: cit.CI_Citation
    amendmentNumber: Optional[gco.CharacterString] = None
    fileDecompressionTechnique: Optional[gco.CharacterString] = None
    medium: Optional[list[mrd.MD_Medium]] = field(default_factory=list)
    formatDistributor: Optional[list[mrd.MD_Distributor]] = field(
        default_factory=list
    )


@dataclass
class MD_StandardOrderProcess:
    fees: Optional[gco.CharacterString] = None
    plannedAvailableDateTime: Optional[gco.DateTime] = None
    orderingInstructions: Optional[gco.CharacterString] = None
    turnaround: Optional[gco.CharacterString] = None
    orderOptionsType: Optional[gco.RecordType] = None
    orderOptions: Optional[gco.Record] = None


@dataclass
class MD_Distribution:
    description: Optional[gco.CharacterString] = None
    distributionFormat: Optional[list[mrd.MD_Format]] = field(
        default_factory=list
    )
    distributor: Optional[list[mrd.MD_Distributor]] = field(
        default_factory=list
    )
    transferOptions: Optional[list[mrd.MD_DigitalTransferOptions]] = field(
        default_factory=list
    )
