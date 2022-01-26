from django import forms
from django.test import TestCase
from edc_appointment.constants import INCOMPLETE_APPT
from edc_constants.constants import INCOMPLETE
from edc_utils import get_utcnow
from model_bakery import baker

from mocca_screening.constants import HIV_CLINIC
from mocca_subject.forms.indicators_form import IndicatorsFormValidator

from ..mocca_test_case_mixin import MoccaTestCaseMixin


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

    def test_weight_height_required_at_baseline(self):
        data = {
            "subject_visit": self.subject_visit,
            "report_datetime": self.subject_visit.report_datetime,
            "crf_status": INCOMPLETE,
            "weight": None,
            "height": None,
        }
        form_validator = IndicatorsFormValidator(cleaned_data=data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("weight", form_validator._errors)

        data.update({"weight": 65, "height": None})
        form_validator = IndicatorsFormValidator(cleaned_data=data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn("height", form_validator._errors)

        data.update({"weight": 65, "height": 120})
        form_validator = IndicatorsFormValidator(cleaned_data=data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertNotIn("weight", form_validator._errors)
        self.assertNotIn("height", form_validator._errors)

    def test_weight_height_not_required_if_not_baseline(self):
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
