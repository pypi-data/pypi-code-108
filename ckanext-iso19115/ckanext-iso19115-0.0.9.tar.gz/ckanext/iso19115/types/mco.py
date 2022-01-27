from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_Constraints:
    useLimitation: list[str] = field(default_factory=list)
    constraintApplicationScope: Optional[mcc.MD_Scope] = None
    graphic: list[mcc.MD_BrowseGraphic] = field(default_factory=list)
    reference: list[cit.CI_Citation] = field(default_factory=list)
    releasability: Optional[MD_Releasability] = None
    responsibleParty: list[cit.CI_Responsibility] = field(default_factory=list)


@dataclass
class MD_RestrictionCode(Codelist):
    pass


@dataclass
class MD_Releasability:
    addressee: list[cit.CI_Responsibility] = field(default_factory=list)
    statement: Optional[str] = None
    disseminationConstraints: list[Codelist[mco.MD_RestrictionCode]] = field(
        default_factory=list
    )
