from canvas_workflow_kit.value_set.value_set import ValueSet
from canvas_workflow_kit.value_set.v2020 import KidneyFailure as v2020KidneyFailure


class KidneyFailure(v2020KidneyFailure):
    """
    Added N1830-N1832 per MRHS request
    """

    OID = '2.16.840.1.113883.3.464.1003.109.12.1028'
    VALUE_SET_NAME = 'Kidney Failure'
    EXPANSION_VERSION = 'eCQM Update 2019-05-10 with a few additions'

    ICD10CM = {
        'N170', 'N171', 'N172', 'N178', 'N179', 'N181', 'N182', 'N183', 'N184', 'N185', 'N186',
        'N189', 'N19', 'N1830', 'N1831', 'N1832'
    }


# @canvas-adr-0006
class Hcc005v1AnnualWellnessVisit(ValueSet):
    VALUE_SET_NAME = 'Annual Wellness Visit'
    EXPANSION_VERSION = 'CanvasHCC Update 2019-11-04'

    HCPCS = {
        'G0438',
        'G0439',
        'G0402',
        '99387',
        '99397',
    }


# @canvas-adr-0006
class CMS125v6Tomography(ValueSet):
    VALUE_SET_NAME = 'Tomography'
    EXPANSION_VERSION = 'Update 2019-08-01'

    LOINC = {
        '72142-3',
    }


# @canvas-adr-0006
class CMS130v6CtColonography(ValueSet):
    VALUE_SET_NAME = 'Ct Colonography'
    EXPANSION_VERSION = 'Update 2019-08-01'

    LOINC = {
        '79101-2',
    }


class CMS134v6Dialysis(ValueSet):
    VALUE_SET_NAME = 'CMS 134v6 Dialysis'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-12-05'

    ICD10CM = {
        'Z992',
    }

    SNOMEDCT = {
        '207RN0300X',
        '2080P0210X',
    }


class LabReportCreatinine(ValueSet):
    VALUE_SET_NAME = 'Lab Report Creatinine'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-04'

    LOINC = {
        '2160-0',
    }


class DiabetesWithoutComplication(ValueSet):
    VALUE_SET_NAME = 'Diabetes Without Complication'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-16'

    ICD10CM = {
        'E119',
    }


class DiabetesEyeConditionSuspect(ValueSet):
    VALUE_SET_NAME = 'Diabetes Eye Condition suspect'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-16'

    ICD10CM = {
        'H28',
        'H36',
    }


class DiabetesEyeClassConditionSuspect(ValueSet):
    VALUE_SET_NAME = 'Diabetes Eye Class Condition suspect'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-16'

    ICD10CM = {
        'H35\d*',
    }


class DiabetesNeurologicConditionSuspect(ValueSet):
    VALUE_SET_NAME = 'Diabetes Neurologic Condition suspect'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-16'

    ICD10CM = {
        'G63',
        'G737',
        'G53',
    }


class DiabetesRenalConditionSuspect(ValueSet):
    VALUE_SET_NAME = 'Diabetes Renal Condition suspect'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-16'

    ICD10CM = {
        'N181',
        'N182',
        'N183',
        'N184',
        'N185',
        'N186',
        'N189',
    }


class DiabetesCirculatoryClassConditionSuspect(ValueSet):
    VALUE_SET_NAME = 'Diabetes Circulatory Class Condition suspect'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-16'

    ICD10CM = {
        'I73\d*',
        'I70\d*',
        'I71\d*',
        'I79\d*',
    }


class DiabetesOtherClassConditionSuspect(ValueSet):
    VALUE_SET_NAME = 'Diabetes Other Class Condition suspect'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-16'

    ICD10CM = {
        'M14\d*',
        'L97\d*',
        'L984\d*',
    }


class DysrhythmiaClassConditionSuspect(ValueSet):
    VALUE_SET_NAME = 'Dysrhythmia Class Condition suspect'
    EXPANSION_VERSION = 'CanvasHCC Update 2018-10-18'

    ICD10CM = {
        'I42\d*',
        'I47\d*',
        'I48\d*',
        'I49\d*',
    }


class Covid19QuestionnaireSymptomaticSurveillance(ValueSet):
    VALUE_SET_NAME = 'Covid19 Questionnaire Symptomatic Surveillance'
    EXPANSION_VERSION = 'CanvasCCP Update 2020-03-19'

    CANVAS = {
        'CANVAS0001',
    }


class Covid19QuestionnaireHighRiskOutreach(ValueSet):
    VALUE_SET_NAME = 'Covid19 Questionnaire High Risk Outreach'
    EXPANSION_VERSION = 'CanvasCCP Update 2020-03-24'

    CANVAS = {
        'CANVAS0006',
    }
