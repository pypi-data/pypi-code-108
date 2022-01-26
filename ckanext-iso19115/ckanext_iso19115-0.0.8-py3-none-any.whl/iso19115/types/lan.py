from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class LanguageCode(Codelist):
    pass


@dataclass
class CountryCode(Codelist):
    pass


@dataclass
class MD_CharacterSetCode(Codelist):
    pass


@dataclass
class PT_Locale:
    language: Codelist[lan.LanguageCode]
    country: Optional[Codelist[lan.CountryCode]] = None
    characterEncoding: Optional[Codelist[lan.MD_CharacterSetCode]] = "UTF-8"
