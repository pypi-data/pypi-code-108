from __future__ import annotations

from dataclasses import Field, dataclass, field
from typing import Optional

from .base import Codelist

from . import *


@dataclass
class DQ_EvaluationMethodTypeCode(Codelist):
    pass


@dataclass
class QualityResultFile:
    fileName: gcx.FileName
    fileType: gcx.MimeFileType
    fileDescription: gco.CharacterString
    fileFormat: mrd.MD_Format


@dataclass
class DQ_StandaloneQualityReportInformation:
    reportReference: cit.CI_Citation
    abstract: gco.CharacterString
    elementReport: Optional[list[mdq.AbstractDQ_Element]] = field(
        default_factory=list
    )


@dataclass
class DQ_DataQuality:
    scope: mcc.MD_Scope
    standaloneQualityReport: Optional[
        mdq.DQ_StandaloneQualityReportInformation
    ] = None
    report: list[mdq.AbstractDQ_Element] = field(default_factory=list)


@dataclass
class DQ_EvaluationMethod:
    dateTime: Optional[list[gco.DateTime]] = field(default_factory=list)
    evaluationMethodDescription: Optional[gco.CharacterString] = None
    evaluationProcedure: Optional[cit.CI_Citation] = None
    referenceDoc: Optional[list[cit.CI_Citation]] = field(default_factory=list)
    evaluationMethodType: Optional[
        Codelist[mdq.DQ_EvaluationMethodTypeCode]
    ] = None


@dataclass
class DQ_MeasureReference:
    measureIdentification: Optional[mcc.MD_Identifier] = None
    nameOfMeasure: Optional[list[gco.CharacterString]] = field(
        default_factory=list
    )
    measureDescription: Optional[gco.CharacterString] = None


@dataclass
class AbstractDQ_Element:
    dateTime: Optional[list[gco.DateTime]] = field(default_factory=list)
    standaloneQualityReportDetails: Optional[gco.CharacterString] = None
    measure: Optional[mdq.DQ_MeasureReference] = None
    evaluationMethod: Optional[mdq.DQ_EvaluationMethod] = None
    result: list[mdq.AbstractDQ_Result] = field(default_factory=list)
    derivedElement: Optional[list[mdq.AbstractDQ_Element]] = field(
        default_factory=list
    )


@dataclass
class DQ_DomainConsistency(AbstractDQ_Element):
    pass


@dataclass
class DQ_TemporalValidity(AbstractDQ_Element):
    pass


@dataclass
class DQ_GriddedDataPositionalAccuracy(AbstractDQ_Element):
    pass


@dataclass
class DQ_TopologicalConsistency(AbstractDQ_Element):
    pass


@dataclass
class DQ_Confidence(AbstractDQ_Element):
    relatedElement: Optional[list[mdq.AbstractDQ_Element]] = field(
        default_factory=list
    )


@dataclass
class DQ_NonQuantitativeAttributeCorrectness(AbstractDQ_Element):
    pass


@dataclass
class DQ_ConceptualConsistency(AbstractDQ_Element):
    pass


@dataclass
class DQ_CompletenessCommission(AbstractDQ_Element):
    pass


@dataclass
class DQ_AccuracyOfATimeMeasurement(AbstractDQ_Element):
    pass


@dataclass
class DQ_AbsoluteExternalPositionalAccuracy(AbstractDQ_Element):
    pass


@dataclass
class DQ_Representativity(AbstractDQ_Element):
    pass
    relatedElement: Optional[list[mdq.AbstractDQ_Element]] = field(
        default_factory=list
    )


@dataclass
class DQ_QuantitativeAttributeAccuracy(AbstractDQ_Element):
    pass


@dataclass
class DQ_UsabilityElement(AbstractDQ_Element):
    pass


@dataclass
class DQ_FormatConsistency(AbstractDQ_Element):
    pass


@dataclass
class DQ_TemporalConsistency(AbstractDQ_Element):
    pass


@dataclass
class DQ_RelativeInternalPositionalAccuracy(AbstractDQ_Element):
    pass


@dataclass
class DQ_CompletenessOmission(AbstractDQ_Element):
    pass


@dataclass
class DQ_Homogeneity(AbstractDQ_Element):
    pass
    relatedElement: Optional[list[mdq.AbstractDQ_Element]] = field(
        default_factory=list
    )


@dataclass
class DQ_ThematicClassificationCorrectness(AbstractDQ_Element):
    pass


@dataclass
class AbstractDQ_Result:
    dateTime: Optional[gco.DateTime] = None
    resultScope: Optional[mcc.MD_Scope] = None


@dataclass
class QE_CoverageResult(AbstractDQ_Result):
    spatialRepresentationType: Codelist[
        mcc.MD_SpatialRepresentationTypeCode
    ] = None
    resultFile: mdq.QualityResultFile = None
    resultSpatialRepresentation: mcc.Abstract_SpatialRepresentation = None
    resultContentDescription: mcc.Abstract_ContentInformation = None
    resultFormat: mrd.MD_Format = None


@dataclass
class DQ_ConformanceResult(AbstractDQ_Result):
    specification: cit.CI_Citation = None
    explanation: Optional[gco.CharacterString] = None
    # pass: gco.Boolean


@dataclass
class DQ_DescriptiveResult(AbstractDQ_Result):
    statement: gco.CharacterString = None


@dataclass
class DQ_QuantitativeResult(AbstractDQ_Result):
    value: list[gco.Record] = field(default_factory=list)
    valueUnit: Optional[gml.UnitDefinition] = None
    valueRecordType: Optional[gco.RecordType] = None
