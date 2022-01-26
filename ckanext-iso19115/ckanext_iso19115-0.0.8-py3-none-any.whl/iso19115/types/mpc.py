from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_PortrayalCatalogueReference:
    portrayalCatalogueCitation: list[cit.CI_Citation] = field(
        default_factory=list
    )
