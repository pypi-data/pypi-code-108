from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_Resolution:
    ...


@dataclass
class MD_KeywordTypeCode(Codelist):
    pass


@dataclass
class DS_AssociationTypeCode(Codelist):
    pass


@dataclass
class DS_InitiativeTypeCode(Codelist):
    pass


@dataclass
class MD_Keywords:
    keyword: list[gco.CharacterString] = field(default_factory=list)
    type: Optional[Codelist[mri.MD_KeywordTypeCode]] = None
    thesaurusName: Optional[cit.CI_Citation] = None
    keywordClass: Optional[MD_KeywordClass] = None


@dataclass
class MD_KeywordClass:
    className: gco.CharacterString
    ontology: cit.CI_Citation
    conceptIdentifier: Optional[mcc.URI] = None


@dataclass
class MD_Usage:
    specificUsage: gco.CharacterString
    usageDateTime: Optional[list[gml.AbstractTimePrimitive]] = field(
        default_factory=list
    )
    userDeterminedLimitations: Optional[gco.CharacterString] = None
    userContactInfo: Optional[list[cit.CI_Responsibility]] = field(
        default_factory=list
    )
    response: Optional[list[gco.CharacterString]] = field(default_factory=list)
    additionalDocumentation: Optional[list[cit.CI_Citation]] = field(
        default_factory=list
    )
    identifiedIssues: Optional[cit.CI_Citation] = None


@dataclass
class MD_AssociatedResource:
    name: Optional[cit.CI_Citation]
    associationType: Codelist[mri.DS_AssociationTypeCode]
    initiativeType: Optional[Codelist[mri.DS_InitiativeTypeCode]] = None
    metadataReference: Optional[cit.CI_Citation] = None


from .mcc import Abstract_ResourceDescription


@dataclass
class MD_DataIdentification(Abstract_ResourceDescription):
    defaultLocale: Optional[lan.PT_Locale] = None
    otherLocale: Optional[list[lan.PT_Locale]] = field(default_factory=list)
    environmentDescription: Optional[gco.CharacterString] = None
    supplementalInformation: Optional[gco.CharacterString] = None
