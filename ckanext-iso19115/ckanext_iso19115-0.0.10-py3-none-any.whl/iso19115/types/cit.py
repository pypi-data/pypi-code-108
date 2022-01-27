from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class CI_DateTypeCode(Codelist):
    pass


@dataclass
class CI_TelephoneTypeCode(Codelist):
    pass


@dataclass
class CI_OnLineFunctionCode(Codelist):
    pass


@dataclass
class CI_Date:
    date: Union[gco.Date, gco.DateTime]
    dateType: Codelist[cit.CI_DateTypeCode]


@dataclass
class CI_Telephone:
    number: gco.CharacterString
    numberType: Optional[Codelist[cit.CI_TelephoneTypeCode]] = None


@dataclass
class CI_Address:
    deliveryPoint: list[gco.CharacterString] = field(default_factory=list)
    city: Optional[gco.CharacterString] = None
    administrativeArea: Optional[gco.CharacterString] = None
    postalCode: Optional[gco.CharacterString] = None
    country: Optional[gco.CharacterString] = None
    electronicMailAddress: list[gco.CharacterString] = field(
        default_factory=list
    )


@dataclass
class CI_OnlineResource:
    linkage: gco.CharacterString
    protocol: Optional[gco.CharacterString] = None
    applicationProfile: Optional[gco.CharacterString] = None
    name: Optional[gco.CharacterString] = None
    description: Optional[gco.CharacterString] = None
    function: Optional[Codelist[cit.CI_OnLineFunctionCode]] = None
    protocolRequest: Optional[gco.CharacterString] = None


@dataclass
class CI_Contact:
    phone: list[cit.CI_Telephone] = field(default_factory=list)
    address: list[cit.CI_Address] = field(default_factory=list)
    onlineResource: list[cit.CI_OnlineResource] = field(default_factory=list)
    hoursOfService: list[str] = field(default_factory=list)
    contactInstructions: Optional[str] = None
    contactType: Optional[str] = None


@dataclass
class CI_RoleCode(Codelist):
    pass


@dataclass
class CI_PresentationFormCode(Codelist):
    pass


@dataclass
class CI_Responsibility:
    role: Codelist[cit.CI_RoleCode]
    # cit:extent
    party: list[AbstractCI_Party] = field(default_factory=list)


@dataclass
class CI_Series:
    name: Optional[str] = None
    issueIdentification: Optional[str] = None
    page: Optional[str] = None


@dataclass
class AbstractCI_Party:
    name: gco.CharacterString = None
    contactInfo: Optional[list[CI_Contact]] = field(default_factory=list)
    partyIdentifier: Optional[list[mcc.MD_Identifier]] = field(
        default_factory=list
    )


@dataclass
class CI_Individual(AbstractCI_Party):
    positionName: Optional[gco.CharacterString] = None


@dataclass
class CI_Organisation(AbstractCI_Party):
    logo: Optional[list[mcc.MD_BrowseGraphic]] = field(default_factory=list)
    individual: Optional[list[CI_Individual]] = field(default_factory=list)


@dataclass
class CI_Citation:
    title: gco.CharacterString
    alternateTitle: Optional[list[gco.CharacterString]] = field(
        default_factory=list
    )
    date: Optional[list[CI_Date]] = field(default_factory=list)
    edition: Optional[gco.CharacterString] = None
    editionDate: Optional[gco.DateTime] = None
    identifier: Optional[list[mcc.MD_Identifier]] = field(default_factory=list)
    citedResponsibleParty: Optional[list[CI_Responsibility]] = field(
        default_factory=list
    )
    presentationForm: Optional[
        list[Codelist[cit.CI_PresentationFormCode]]
    ] = field(default_factory=list)
    series: Optional[CI_Series] = None
    otherCitationDetails: Optional[list[gco.CharacterString]] = field(
        default_factory=list
    )
    ISBN: Optional[gco.CharacterString] = None
    ISSN: Optional[gco.CharacterString] = None
    onlineResource: Optional[list[CI_OnlineResource]] = field(
        default_factory=list
    )
    graphic: Optional[list[mcc.MD_BrowseGraphic]] = field(default_factory=list)
