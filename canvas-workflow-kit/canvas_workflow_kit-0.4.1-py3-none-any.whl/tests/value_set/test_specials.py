from unittest import TestCase

from canvas_workflow_kit.value_set.specials import (
    Covid19QuestionnaireSymptomaticSurveillance,
    Covid19QuestionnaireHighRiskOutreach,
    Hcc005v1AnnualWellnessVisit,
    CMS125v6Tomography,
    CMS130v6CtColonography,
    CMS134v6Dialysis,
    LabReportCreatinine,
    DiabetesWithoutComplication,
    DiabetesEyeConditionSuspect,
    DiabetesEyeClassConditionSuspect,
    DiabetesNeurologicConditionSuspect,
    DiabetesRenalConditionSuspect,
    DiabetesCirculatoryClassConditionSuspect,
    DiabetesOtherClassConditionSuspect,
    DysrhythmiaClassConditionSuspect,
)


class TestHcc005v1AnnualWellnessVisit(TestCase):

    def test_set(self):
        expected = {
            'hcpcs': {'99397', 'G0439', 'G0402', '99387', 'G0438'},
        }
        self.assertEqual(expected, Hcc005v1AnnualWellnessVisit.values)


class TestCMS125v6Tomography(TestCase):

    def test_set(self):
        expected = {
            'loinc': {'72142-3'},
        }
        self.assertEqual(expected, CMS125v6Tomography.values)


class TestCMS130v6CtColonography(TestCase):

    def test_set(self):
        expected = {
            'loinc': {'79101-2'},
        }
        self.assertEqual(expected, CMS130v6CtColonography.values)


class TestCMS134v6Dialysis(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {'Z992'},
            'snomedct': {'2080P0210X', '207RN0300X'},
        }
        self.assertEqual(expected, CMS134v6Dialysis.values)


class TestLabReportCreatinine(TestCase):

    def test_set(self):
        expected = {
            'loinc': {'2160-0'},
        }
        self.assertEqual(expected, LabReportCreatinine.values)


class TestDiabetesWithoutComplication(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {'E119'},
        }
        self.assertEqual(expected, DiabetesWithoutComplication.values)


class TestDiabetesEyeConditionSuspect(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {'H28', 'H36'},
        }
        self.assertEqual(expected, DiabetesEyeConditionSuspect.values)


class TestDiabetesEyeClassConditionSuspect(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {r'H35\d*'},
        }
        self.assertEqual(expected, DiabetesEyeClassConditionSuspect.values)


class TestDiabetesNeurologicConditionSuspect(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {'G63', 'G737', 'G53'},
        }
        self.assertEqual(expected, DiabetesNeurologicConditionSuspect.values)


class TestDiabetesRenalConditionSuspect(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {'N181', 'N182', 'N183', 'N184', 'N185', 'N186', 'N189'},
        }
        self.assertEqual(expected, DiabetesRenalConditionSuspect.values)


class TestDiabetesCirculatoryClassConditionSuspect(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {r'I73\d*', r'I70\d*', r'I71\d*', r'I79\d*'},
        }
        self.assertEqual(expected, DiabetesCirculatoryClassConditionSuspect.values)


class TestDiabetesOtherClassConditionSuspect(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {r'M14\d*', r'L97\d*', r'L984\d*'},
        }
        self.assertEqual(expected, DiabetesOtherClassConditionSuspect.values)


class TestDysrhythmiaClassConditionSuspect(TestCase):

    def test_set(self):
        expected = {
            'icd10cm': {r'I42\d*', r'I47\d*', r'I48\d*', r'I49\d*'},
        }
        self.assertEqual(expected, DysrhythmiaClassConditionSuspect.values)


class TestCovid19QuestionnaireSymptomaticSurveillance(TestCase):

    def test_set(self):
        expected = {
            'canvas': {'CANVAS0001'},
        }
        self.assertEqual(expected, Covid19QuestionnaireSymptomaticSurveillance.values)


class TestCovid19QuestionnaireHighRiskOutreach(TestCase):

    def test_set(self):
        expected = {
            'canvas': {'CANVAS0006'},
        }
        self.assertEqual(expected, Covid19QuestionnaireHighRiskOutreach.values)
