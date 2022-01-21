from unittest import TestCase
from canvas_workflow_kit.value_set import v2018


class SDKValueSetTest(TestCase):

    def test_basics(self):
        self.assertTrue(v2018.Diabetes)
        self.assertIn('E1010', v2018.Diabetes.values['icd10cm'])

    def test_or(self):
        diabetes_or_cough = v2018.UpperRespiratoryInfection | v2018.Diabetes
        self.assertIn('E1010', diabetes_or_cough.values['icd10cm'])
        self.assertIn('195708003', diabetes_or_cough.values['snomedct'])

        diabetes_or_cough_or_more = v2018.UpperRespiratoryInfection | v2018.Diabetes | v2018.IschemicVascularDisease
        self.assertIn('E1010', diabetes_or_cough_or_more.values['icd10cm'])
        self.assertIn('195708003', diabetes_or_cough_or_more.values['snomedct'])
        self.assertIn('I70261', diabetes_or_cough_or_more.values['icd10cm'])
