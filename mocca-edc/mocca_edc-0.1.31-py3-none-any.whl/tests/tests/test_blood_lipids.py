from django import forms
from django.test import TestCase, tag
from edc_appointment.constants import INCOMPLETE_APPT
from edc_constants.constants import INCOMPLETE, NO, NOT_APPLICABLE, YES
from edc_dx_review.constants import HIV_CLINIC
from edc_reportable import GRADE3, MILLIMOLES_PER_LITER
from edc_utils import get_utcnow
from model_bakery import baker

from mocca_subject.forms import BloodResultsLipidFormValidator
from mocca_subject.forms.indicators_form import IndicatorsFormValidator

from ..mocca_test_case_mixin import MoccaTestCaseMixin


@tag("ldl")
class TestIndicators(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_screening = self.get_subject_screening(
            report_datetime=get_utcnow(), clinic_type=HIV_CLINIC
        )
        self.subject_consent = self.get_subject_consent(
            subject_screening=self.subject_screening, clinic_type=HIV_CLINIC
        )
        self.subject_visit = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )
        baker.make("mocca_subject.clinicalreviewbaseline", subject_visit=self.subject_visit)

    def test_blood_lipids_form_baseline(self):
        data = {
            "subject_visit": self.subject_visit,
            "report_datetime": self.subject_visit.report_datetime,
            "crf_status": INCOMPLETE,
            "ldl": 10000,
            "ldl_units": MILLIMOLES_PER_LITER,
            "ldl_abnormal": YES,
            "ldl_reportable": GRADE3,
        }
        form_validator = BloodResultsLipidFormValidator(cleaned_data=data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertDictEqual({}, form_validator._errors)

    def test_blood_lipids_form_chol_g3_baseline(self):
        data = {
            "subject_visit": self.subject_visit,
            "report_datetime": self.subject_visit.report_datetime,
            "crf_status": INCOMPLETE,
            "chol": 8.0,
            "chol_units": MILLIMOLES_PER_LITER,
            "chol_abnormal": YES,
            "chol_reportable": GRADE3,
        }
        form_validator = BloodResultsLipidFormValidator(cleaned_data=data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertDictEqual({}, form_validator._errors)

    def test_blood_lipids_form_chol_normal_baseline(self):
        data = {
            "subject_visit": self.subject_visit,
            "report_datetime": self.subject_visit.report_datetime,
            "crf_status": INCOMPLETE,
            "chol": 6.0,
            "chol_units": MILLIMOLES_PER_LITER,
            "chol_abnormal": NO,
            "chol_reportable": NOT_APPLICABLE,
        }
        form_validator = BloodResultsLipidFormValidator(cleaned_data=data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertDictEqual({}, form_validator._errors)

    def test_blood_lipids_form(self):
        self.subject_visit.appointment.appt_status = INCOMPLETE_APPT
        self.subject_visit.appointment.save()
        self.subject_visit.appointment.refresh_from_db()

        subject_visit = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
            visit_code=self.subject_visit.appointment.next.visit_code,
        )
        data = {
            "subject_visit": subject_visit,
            "report_datetime": subject_visit.report_datetime,
            "crf_status": INCOMPLETE,
            "weight": None,
            "height": None,
        }
        form_validator = IndicatorsFormValidator(cleaned_data=data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertNotIn("weight", form_validator._errors)
        self.assertNotIn("height", form_validator._errors)
