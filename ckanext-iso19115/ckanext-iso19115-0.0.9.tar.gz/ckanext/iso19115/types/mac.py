from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import Codelist

if TYPE_CHECKING:
    from . import *


@dataclass
class MI_InstrumentationEventTypeCode(Codelist):
    pass


@dataclass
class MI_OperationTypeCode(Codelist):
    pass


@dataclass
class MI_ObjectiveTypeCode(Codelist):
    pass


@dataclass
class MI_TriggerCode(Codelist):
    pass


@dataclass
class MI_ContextCode(Codelist):
    pass


@dataclass
class MI_SequenceCode(Codelist):
    pass


@dataclass
class MI_GeometryTypeCode(Codelist):
    pass


@dataclass
class MI_PriorityCode(Codelist):
    pass


@dataclass
class MI_Revision:
    description: Optional[gco.CharacterString] = None
    author: cit.CI_Responsibility = None
    dateInfo: cit.CI_Date = None


@dataclass
class MI_Objective:
    identifier: list[mcc.MD_Identifier] = field(default_factory=list)
    priority: Optional[gco.CharacterString] = None
    type: Optional[list[Codelist[mac.MI_ObjectiveTypeCode]]] = field(
        default_factory=list
    )
    function: Optional[list[gco.CharacterString]] = field(default_factory=list)
    extent: Optional[list[gex.EX_Extent]] = field(default_factory=list)
    sensingInstrument: Optional[list[mac.MI_Instrument]] = field(
        default_factory=list
    )
    # pass: Optional[list[mac.MI_PlatformPass]] = field(default_factory=list)
    objectiveOccurence: list[mac.MI_Event] = field(default_factory=list)


@dataclass
class MI_Plan:
    type: Optional[Codelist[mac.MI_GeometryTypeCode]] = None
    status: Codelist[mcc.MD_ProgressCode] = None
    citation: cit.CI_Citation = None
    operation: Optional[list[mac.MI_Operation]] = field(default_factory=list)
    satisfiedRequirement: Optional[list[mac.MI_Requirement]] = field(
        default_factory=list
    )


@dataclass
class MI_PlatformPass:
    identifier: mcc.MD_Identifier
    extent: Optional[gml.AbstractGeometry] = None
    relatedEvent: Optional[list[mac.MI_Event]] = field(default_factory=list)


@dataclass
class MI_Event:
    identifier: mcc.MD_Identifier
    trigger: Codelist[mac.MI_TriggerCode]
    context: Codelist[mac.MI_ContextCode]
    sequence: Codelist[mac.MI_SequenceCode]
    time: gco.DateTime
    relatedPass: Optional[mac.MI_PlatformPass] = None
    relatedSensor: Optional[list[mac.MI_Instrument]] = field(
        default_factory=list
    )
    expectedObjective: Optional[list[mac.MI_Objective]] = field(
        default_factory=list
    )


@dataclass
class MI_Platform:
    citation: Optional[list[cit.CI_Citation]] = field(default_factory=list)
    identifier: mcc.MD_Identifier = None
    description: gco.CharacterString = None
    sponsor: Optional[list[cit.CI_Responsibility]] = field(
        default_factory=list
    )
    instrument: list[mac.MI_Instrument] = field(default_factory=list)
    otherPropertyType: Optional[gco.RecordType] = None
    otherProperty: Optional[gco.Record] = None
    history: Optional[list[mac.MI_InstrumentationEventList]] = field(
        default_factory=list
    )


@dataclass
class MI_Sensor:
    citation: Optional[list[cit.CI_Citation]] = field(default_factory=list)
    identifier: mcc.MD_Identifier = None
    type: gco.CharacterString = None
    description: Optional[gco.CharacterString] = None
    mountedOn: Optional[mac.MI_Platform] = None
    otherPropertyType: Optional[gco.RecordType] = None
    otherProperty: Optional[gco.Record] = None
    content: Optional[mcc.Abstract_ContentInformation] = None
    sensor: Optional[list[mac.MI_Sensor]] = field(default_factory=list)
    history: Optional[list[mac.MI_InstrumentationEventList]] = field(
        default_factory=list
    )
    hosted: Optional[list[mac.MI_Instrument]] = field(default_factory=list)


@dataclass
class MI_InstrumentationEvent:
    citation: Optional[list[cit.CI_Citation]] = field(default_factory=list)
    description: gco.CharacterString = None
    extent: Optional[list[gex.EX_Extent]] = field(default_factory=list)
    type: list[Codelist[mac.MI_InstrumentationEventTypeCode]] = field(
        default_factory=list
    )
    revisionHistory: Optional[list[mac.MI_Revision]] = field(
        default_factory=list
    )


@dataclass
class MI_InstrumentationEventList:
    citation: cit.CI_Citation
    description: gco.CharacterString
    locale: Optional[lan.PT_Locale] = None
    metadataConstraints: Optional[list[mco.MD_Constraints]] = field(
        default_factory=list
    )
    instrumentationEvent: list[mac.MI_InstrumentationEvent] = field(
        default_factory=list
    )


@dataclass
class MI_Instrument:
    citation: Optional[list[cit.CI_Citation]] = field(default_factory=list)
    identifier: mcc.MD_Identifier = None
    type: gco.CharacterString = None
    description: Optional[gco.CharacterString] = None
    mountedOn: Optional[mac.MI_Platform] = None
    otherPropertyType: Optional[gco.RecordType] = None
    otherProperty: Optional[gco.Record] = None
    # content: Optional[mcc.Abstract_ContentInformation] = None
    sensor: Optional[list[mac.MI_Sensor]] = field(default_factory=list)
    history: Optional[list[mac.MI_InstrumentationEventList]] = field(
        default_factory=list
    )


@dataclass
class MI_Operation:
    description: Optional[gco.CharacterString] = None
    citation: Optional[cit.CI_Citation] = None
    identifier: Optional[mcc.MD_Identifier] = None
    status: Codelist[mcc.MD_ProgressCode] = None
    type: Optional[Codelist[mac.MI_OperationTypeCode]] = None
    parentOperation: Optional[mac.MI_Operation] = None
    childOperation: Optional[list[mac.MI_Operation]] = field(
        default_factory=list
    )
    platform: Optional[list[mac.MI_Platform]] = field(default_factory=list)
    objective: Optional[list[mac.MI_Objective]] = field(default_factory=list)
    plan: Optional[mac.MI_Plan] = None
    significantEvent: Optional[list[mac.MI_Event]] = field(
        default_factory=list
    )
    otherPropertyType: Optional[gco.RecordType] = None
    otherProperty: Optional[gco.Record] = None


@dataclass
class MI_AcquisitionInformation:
    scope: mcc.MD_Scope
    instrument: Optional[list[mac.MI_Instrument]] = field(default_factory=list)
    operation: Optional[list[mac.MI_Operation]] = field(default_factory=list)
    platform: Optional[list[mac.MI_Platform]] = field(default_factory=list)
    acquisitionPlan: Optional[list[mac.MI_Plan]] = field(default_factory=list)
    objective: Optional[list[mac.MI_Objective]] = field(default_factory=list)
    acquisitionRequirement: Optional[list[mac.MI_Requirement]] = field(
        default_factory=list
    )
    environmentalConditions: Optional[mac.MI_EnvironmentalRecord] = None


@dataclass
class MI_Requirement:
    citation: Optional[cit.CI_Citation] = None
    identifier: mcc.MD_Identifier = None
    requestor: list[cit.CI_Responsibility] = field(default_factory=list)
    recipient: list[cit.CI_Responsibility] = field(default_factory=list)
    priority: Codelist[mac.MI_PriorityCode] = None
    requestedDate: mac.MI_RequestedDate = None
    expiryDate: gco.DateTime = None
    satisifiedPlan: Optional[list[mac.MI_Plan]] = field(default_factory=list)


@dataclass
class MI_EnvironmentalRecord:
    averageAirTemperature: gco.Real
    maxRelativeHumidity: gco.Real
    maxAltitude: gco.Real
    meterologicalConditions: gco.CharacterString
    solarAzimuth: gco.Real
    solarElevation: gco.Real


@dataclass
class MI_RequestedDate:
    requestedDateOfCollection: gco.DateTime
    latestAcceptableDate: gco.DateTime
