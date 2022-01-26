from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from . import *


@dataclass
class LI_ProcessStep:
    description: gco.CharacterString
    rationale: Optional[gco.CharacterString] = None
    stepDateTime: Optional[gml.AbstractTimePrimitive] = None
    processor: Optional[list[cit.CI_Responsibility]] = field(
        default_factory=list
    )
    reference: Optional[list[cit.CI_Citation]] = field(default_factory=list)
    scope: Optional[mcc.MD_Scope] = None
    source: Optional[list[mrl.LI_Source]] = field(default_factory=list)


@dataclass
class LI_Source:
    description: Optional[gco.CharacterString] = None
    sourceSpatialResolution: Optional[mri.MD_Resolution] = None
    sourceReferenceSystem: Optional[mrs.MD_ReferenceSystem] = None
    sourceCitation: Optional[cit.CI_Citation] = None
    sourceMetadata: Optional[list[cit.CI_Citation]] = field(
        default_factory=list
    )
    scope: Optional[mcc.MD_Scope] = None
    sourceStep: Optional[list[mrl.LI_ProcessStep]] = field(
        default_factory=list
    )


@dataclass
class LI_Lineage:
    statement: Optional[gco.CharacterString] = None
    scope: Optional[mcc.MD_Scope] = None
    additionalDocumentation: Optional[list[cit.CI_Citation]] = field(
        default_factory=list
    )
    source: Optional[list[mrl.LI_Source]] = field(default_factory=list)
    processStep: Optional[list[mrl.LI_ProcessStep]] = field(
        default_factory=list
    )
