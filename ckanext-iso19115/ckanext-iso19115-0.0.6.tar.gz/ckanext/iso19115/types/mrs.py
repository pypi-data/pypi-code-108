from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_ReferenceSystemTypeCode(Codelist):
    print()


@dataclass
class MD_ReferenceSystem:

    referenceSystemIdentifier: Optional[mcc.MD_Identifier] = None
    referenceSystemType: Optional[
        Codelist[mrs.MD_ReferenceSystemTypeCode]
    ] = None
