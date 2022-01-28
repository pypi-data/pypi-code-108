from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional, Union

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class MD_MetadataScope:
    resourceScope: Codelist[mcc.MD_ScopeCode]
    name: Optional[gco.CharacterString] = None


@dataclass
class MD_Metadata:
    metadataIdentifier: Optional[mcc.MD_Identifier] = None
    defaultLocale: Optional[lan.PT_Locale] = None
    parentMetadata: Optional[cit.CI_Citation] = None
    metadataScope: Optional[list[mdb.MD_MetadataScope]] = field(
        default_factory=list
    )

    contact: list[cit.CI_Responsibility] = field(default_factory=list)
    dateInfo: list[cit.CI_Date] = field(default_factory=list)

    metadataStandard: Optional[list[cit.CI_Citation]] = field(
        default_factory=list
    )
    metadataProfile: Optional[list[cit.CI_Citation]] = field(
        default_factory=list
    )
    alternativeMetadataReference: Optional[list[cit.CI_Citation]] = field(
        default_factory=list
    )

    otherLocale: Optional[list[lan.PT_Locale]] = field(default_factory=list)
    metadataLinkage: Optional[list[cit.CI_OnlineResource]] = field(
        default_factory=list
    )
    spatialRepresentationInfo: Optional[
        list[mcc.Abstract_SpatialRepresentation]
    ] = field(default_factory=list)
    referenceSystemInfo: Optional[list[mrs.MD_ReferenceSystem]] = field(
        default_factory=list
    )
    metadataExtensionInfo: Optional[
        list[mex.MD_MetadataExtensionInformation]
    ] = field(default_factory=list)

    identificationInfo: list[mcc.Abstract_ResourceDescription] = field(
        default_factory=list
    )

    contentInfo: Optional[list[mcc.Abstract_ContentInformation]] = field(
        default_factory=list
    )
    distributionInfo: Optional[list[mrd.MD_Distribution]] = field(
        default_factory=list
    )
    dataQualityInfo: Optional[list[mdq.DQ_DataQuality]] = field(
        default_factory=list
    )
    resourceLineage: Optional[list[mrl.LI_Lineage]] = field(
        default_factory=list
    )
    portrayalCatalogueInfo: Optional[
        list[mpc.MD_PortrayalCatalogueReference]
    ] = field(default_factory=list)
    metadataConstraints: Optional[list[mco.MD_Constraints]] = field(
        default_factory=list
    )
    applicationSchemaInfo: Optional[
        list[mas.MD_ApplicationSchemaInformation]
    ] = field(default_factory=list)
    metadataMaintenance: Optional[mmi.MD_MaintenanceInformation] = None
    acquisitionInformation: Optional[
        list[mac.MI_AcquisitionInformation]
    ] = field(default_factory=list)

    def add_dateInfo(self, date: cit.CI_Date):
        self.dateInfo.append(date)

    def add_contact(self, contact: cit.CI_Responsibility):
        self.contact.append(contact)

    def add_identificationInfo(
        self,
        ident: Union[mri.MD_DataIdentification, srv.SV_ServiceIdentification],
    ):
        self.identificationInfo.append(ident)
