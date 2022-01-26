from django.test import TestCase
from edc_constants.constants import FEMALE, INCOMPLETE, MALE, NO, NOT_APPLICABLE, YES
from edc_utils import get_utcnow
from pytz import timezone

from mocca_screening.constants import (
    DIABETES_CLINIC,
    HIV_CLINIC,
    HYPERTENSION_CLINIC,
    NCD_CLINIC,
)
from mocca_subject.forms import ClinicalReviewBaselineForm

from ..mocca_test_case_mixin import MoccaTestCaseMixin


def get_now():
    return get_utcnow().astimezone(timezone("Africa/Kampala"))


class TestClinicalReviewBaseline(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        # hiv clinic
        self.subject_screening_hiv = self.get_subject_screening(
            report_datetime=get_utcnow(),
            clinic_type=HIV_CLINIC,
            gender=FEMALE,
        )
        self.subject_consent_hiv = self.get_subject_consent(
            subject_screening=self.subject_screening_hiv,
            clinic_type=HIV_CLINIC,
        )
        self.subject_visit_hiv = self.get_subject_visit(
            subject_screening=self.subject_screening_hiv,
            subject_consent=self.subject_consent_hiv,
        )

        # htn clinic
        self.subject_screening_htn = self.get_subject_screening(
            report_datetime=get_utcnow(),
            clinic_type=HYPERTENSION_CLINIC,
            gender=MALE,
        )
        self.subject_consent_htn = self.get_subject_consent(
            subject_screening=self.subject_screening_htn,
            clinic_type=HYPERTENSION_CLINIC,
        )
        self.subject_visit_htn = self.get_subject_visit(
            subject_screening=self.subject_screening_htn,
            subject_consent=self.subject_consent_htn,
        )

        # diabetes clinic
        self.subject_screening_dm = self.get_subject_screening(
            report_datetime=get_utcnow(),
            clinic_type=DIABETES_CLINIC,
            gender=FEMALE,
        )
        self.subject_consent_dm = self.get_subject_consent(
            subject_screening=self.subject_screening_dm,
            clinic_type=DIABETES_CLINIC,
        )
        self.subject_visit_dm = self.get_subject_visit(
            subject_screening=self.subject_screening_dm,
            subject_consent=self.subject_consent_dm,
        )

        # NCD clinic
        self.subject_screening_ncd = self.get_subject_screening(
            report_datetime=get_utcnow(),
            clinic_type=NCD_CLINIC,
            gender=MALE,
        )
        self.subject_consent_ncd = self.get_subject_consent(
            subject_screening=self.subject_screening_ncd,
            clinic_type=NCD_CLINIC,
        )
        self.subject_visit_ncd = self.get_subject_visit(
            subject_screening=self.subject_screening_ncd,
            subject_consent=self.subject_consent_ncd,
        )

    def test_form_ok_hiv(self):
        data = {
            "subject_visit": self.subject_visit_hiv.pk,
            "report_datetime": self.subject_visit_hiv.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": YES,
            "hiv_test_ago": "5y",
            "hiv_dx": YES,
            "htn_test": NO,
            "htn_dx": NOT_APPLICABLE,
            "dm_test": NO,
            "dm_test_ago": None,
            "dm_dx": NOT_APPLICABLE,
            "chol_test": NO,
            "chol_test_ago": None,
            "chol_dx": NOT_APPLICABLE,
            "complications": YES,
        }
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})

    def test_form_ok_hypertensive(self):
        data = {
            "subject_visit": self.subject_visit_htn.pk,
            "report_datetime": self.subject_visit_htn.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": NO,
            "hiv_test_ago": None,
            "hiv_dx": NOT_APPLICABLE,
            "htn_test": YES,
            "htn_test_ago": "1y1m",
            "htn_dx": YES,
            "dm_test": NO,
            "dm_test_ago": None,
            "dm_dx": NOT_APPLICABLE,
            "chol_test": NO,
            "chol_test_ago": None,
            "chol_dx": NOT_APPLICABLE,
            "complications": YES,
        }
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})

    def test_form_ok_dm(self):
        data = {
            "subject_visit": self.subject_visit_dm.pk,
            "report_datetime": self.subject_visit_dm.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": NO,
            "hiv_test_ago": None,
            "hiv_dx": NOT_APPLICABLE,
            "htn_test": NO,
            "htn_test_ago": None,
            "htn_dx": NOT_APPLICABLE,
            "dm_test": YES,
            "dm_test_ago": "1y1m",
            "dm_dx": YES,
            "chol_test": NO,
            "chol_test_ago": None,
            "chol_dx": NOT_APPLICABLE,
            "complications": YES,
        }
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})

    def test_form_ok_chol(self):
        data = {
            "subject_visit": self.subject_visit_dm.pk,
            "report_datetime": self.subject_visit_dm.report_datetime,
            "crf_status": INCOMPLETE,
            "hiv_test": NO,
            "hiv_test_ago": None,
            "hiv_dx": NOT_APPLICABLE,
            "htn_test": NO,
            "htn_test_ago": None,
            "htn_dx": NOT_APPLICABLE,
            "dm_test": NO,
            "dm_test_ago": None,
            "dm_dx": NOT_APPLICABLE,
            "chol_test": YES,
            "chol_test_ago": "1y1m",
            "chol_dx": YES,
            "complications": YES,
        }
        form = ClinicalReviewBaselineForm(data=data)
        form.is_valid()
        self.assertEqual(form._errors, {})
