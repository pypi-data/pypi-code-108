from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from .base import Codelist

from . import gco

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_CoverageContentTypeCode(Codelist):
    pass


@dataclass
class MD_RangeDimension:
    sequenceIdentifier: Optional[gco.MemberName] = None
    description: Optional[gco.CharacterString] = None
    name: Optional[list[mcc.MD_Identifier]] = field(default_factory=list)


@dataclass
class MD_FeatureTypeInfo:
    featureTypeName: gco.ScopedName
    featureInstanceCount: Optional[gco.Integer] = None


@dataclass
class MD_AttributeGroup:
    contentType: list[Codelist[mrc.MD_CoverageContentTypeCode]] = field(
        default_factory=list
    )
    attribute: Optional[list[mrc.MD_RangeDimension]] = field(
        default_factory=list
    )


@dataclass
class MD_FeatureCatalogueDescription:
    complianceCode: Optional[gco.Boolean] = None
    locale: Optional[list[lan.PT_Locale]] = field(default_factory=list)
    includedWithDataset: Optional[gco.Boolean] = None
    featureTypes: Optional[list[mrc.MD_FeatureTypeInfo]] = field(
        default_factory=list
    )
    featureCatalogueCitation: Optional[list[cit.CI_Citation]] = field(
        default_factory=list
    )


@dataclass
class MD_CoverageDescription:
    attributeDescription: gco.RecordType = None
    processingLevelCode: Optional[mcc.MD_Identifier] = None
    attributeGroup: Optional[list[mrc.MD_AttributeGroup]] = field(
        default_factory=list
    )


@dataclass
class MD_FeatureCatalogue:
    featureCatalogue: list[Any] = field(default_factory=list)
