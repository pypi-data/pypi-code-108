from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from . import *


@dataclass
class MD_ApplicationSchemaInformation:
    name: cit.CI_Citation
    schemaLanguage: gco.CharacterString
    constraintLanguage: gco.CharacterString
    schemaAscii: Optional[gco.CharacterString] = None
    graphicsFile: Optional[cit.CI_OnlineResource] = None
    softwareDevelopmentFile: Optional[cit.CI_OnlineResource] = None
    softwareDevelopmentFileFormat: Optional[gco.CharacterString] = None
