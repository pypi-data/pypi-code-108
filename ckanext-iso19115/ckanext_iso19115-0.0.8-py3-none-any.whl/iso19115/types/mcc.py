from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class URI:
    ...


@dataclass
class MD_ProgressCode(Codelist):
    pass


@dataclass
class MD_Identifier:
    authority: Optional[cit.CI_Citation] = None
    code: gco.CharacterString = None
    codeSpace: Optional[gco.CharacterString] = None
    version: Optional[gco.CharacterString] = None
    description: Optional[gco.CharacterString] = None


@dataclass
class MD_BrowseGraphic:
    fileName: gco.CharacterString
    fileDescription: Optional[gco.CharacterString] = None
    fileType: Optional[gco.CharacterString] = None
    imageConstraints: Optional[list[mco.MD_Constraints]] = field(
        default_factory=list
    )
    linkage: Optional[list[cit.CI_OnlineResource]] = field(
        default_factory=list
    )


@dataclass
class MD_ScopeCode(Codelist):
    pass


@dataclass
class MD_Scope:
    level: Codelist[mcc.MD_ScopeCode]
    # extent: list[gex.EX_Extent] = field(default_factory=list)
    levelDescription: list[MD_ScopeDescription] = field(default_factory=list)


@dataclass
class MD_ScopeDescription:
    attributes: str
    features: str
    featureInstances: str
    attributeInstances: str
    dataset: str
    other: str


@dataclass
class MD_SpatialRepresentationTypeCode(Codelist):
    pass


@dataclass
class MD_TopicCategoryCode(Codelist):
    pass


@dataclass
class Abstract_ResourceDescription:
    citation: cit.CI_Citation
    abstract: gco.CharacterString
    purpose: Optional[gco.CharacterString] = None
    credit: Optional[list[gco.CharacterString]] = field(default_factory=list)
    status: Optional[list[Codelist[mcc.MD_ProgressCode]]] = field(
        default_factory=list
    )
    pointOfContact: Optional[list[cit.CI_Responsibility]] = field(
        default_factory=list
    )
    spatialRepresentationType: Optional[
        list[Codelist[mcc.MD_SpatialRepresentationTypeCode]]
    ] = field(default_factory=list)
    spatialResolution: Optional[list[mri.MD_Resolution]] = field(
        default_factory=list
    )
    temporalResolution: Optional[list[gco.TM_PeriodDuration]] = field(
        default_factory=list
    )
    topicCategory: Optional[list[Codelist[mcc.MD_TopicCategoryCode]]] = field(
        default_factory=list
    )
    extent: Optional[list[gex.EX_Extent]] = field(default_factory=list)
    additionalDocumentation: list[cit.CI_Citation] = field(
        default_factory=list
    )
    processingLevel: Optional[mcc.MD_Identifier] = None
    resourceMaintenance: Optional[list[mmi.MD_MaintenanceInformation]] = field(
        default_factory=list
    )
    graphicOverview: Optional[list[mcc.MD_BrowseGraphic]] = field(
        default_factory=list
    )
    resourceFormat: Optional[list[mrd.MD_Format]] = field(default_factory=list)
    descriptiveKeywords: Optional[list[mri.MD_Keywords]] = field(
        default_factory=list
    )
    resourceSpecificUsage: Optional[list[mri.MD_Usage]] = field(
        default_factory=list
    )
    resourceConstraints: Optional[list[mco.MD_Constraints]] = field(
        default_factory=list
    )
    associatedResource: Optional[list[mri.MD_AssociatedResource]] = field(
        default_factory=list
    )


@dataclass
class Abstract_SpatialRepresentation:
    ...
    # |msr:MD_GridSpatialRepresentation [id, uuid] (too deep...)
    # |msr:MD_VectorSpatialRepresentation [id, uuid] (too deep...)


@dataclass
class Abstract_ContentInformation:
    ...
    # |mrc:MD_FeatureCatalogueDescription [id, uuid] (too deep...)
    # |mrc:MD_CoverageDescription [id, uuid] (too deep...)
    # |mrc:MD_FeatureCatalogue [id, uuid] (too deep...)
