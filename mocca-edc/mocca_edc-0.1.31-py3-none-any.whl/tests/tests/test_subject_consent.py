from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase
from edc_constants.constants import FEMALE, MOBILE_NUMBER, NO, YES
from edc_utils import get_utcnow
from pytz import timezone

from mocca_consent.forms import SubjectConsentForm, SubjectConsentFormValidator

from ..mocca_test_case_mixin import MoccaTestCaseMixin


def get_now():
    return get_utcnow().astimezone(timezone("Africa/Kampala"))


class TestSubjectConsent(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.eligibility_datetime = get_utcnow() - relativedelta(days=2)  # yesterday

    def test_form_validator_ok(self):
        subject_screening = self.get_subject_screening(
            eligibility_datetime=self.eligibility_datetime,
            gender=FEMALE,
        )
        consent_datetime = get_now()
        cleaned_data = dict(
            screening_identifier=subject_screening.screening_identifier,
            dob=subject_screening.report_datetime.date()
            - relativedelta(years=subject_screening.age_in_years),
            consent_datetime=consent_datetime,
            identity_type=MOBILE_NUMBER,
            identity="77777777",
            confirm_identity="77777777",
            gender=FEMALE,
        )
        validator = SubjectConsentFormValidator(
            cleaned_data=cleaned_data,
        )
        validator.clean()

    def test_form_validator_consent_before_eligibility_datetime(self):
        subject_screening = self.get_subject_screening(
            eligibility_datetime=self.eligibility_datetime,
            gender=FEMALE,
        )
        consent_datetime = subject_screening.eligibility_datetime - relativedelta(minutes=10)
        consent_datetime = consent_datetime.astimezone(timezone("Africa/Kampala"))
        cleaned_data = dict(
            screening_identifier=subject_screening.screening_identifier,
            dob=subject_screening.report_datetime.date()
            - relativedelta(years=subject_screening.age_in_years),
            consent_datetime=consent_datetime,
            identity_type=MOBILE_NUMBER,
            identity="77777777",
            confirm_identity="77777777",
            gender=FEMALE,
        )
        validator = SubjectConsentFormValidator(
            cleaned_data=cleaned_data,
        )
        self.assertRaises(forms.ValidationError, validator.clean)
        with self.assertRaises(forms.ValidationError) as cm:
            validator.clean()
        self.assertIn("consent_datetime", str(cm.exception))

    def test_form_validator_consent_after_eligibility_datetime(self):
        subject_screening = self.get_subject_screening(
            eligibility_datetime=self.eligibility_datetime,
            gender=FEMALE,
        )
        consent_datetime = subject_screening.eligibility_datetime + relativedelta(minutes=1)
        consent_datetime = consent_datetime.astimezone(timezone("Africa/Kampala"))
        cleaned_data = dict(
            screening_identifier=subject_screening.screening_identifier,
            dob=subject_screening.report_datetime.date()
            - relativedelta(years=subject_screening.age_in_years),
            consent_datetime=consent_datetime,
            identity_type=MOBILE_NUMBER,
            identity="77777777",
            confirm_identity="77777777",
            gender=FEMALE,
        )
        validator = SubjectConsentFormValidator(
            cleaned_data=cleaned_data,
        )
        try:
            validator.clean()
        except forms.ValidationError:
            self.fail("ValidationError unexpectedly raised")

    def test_model_consent(self):
        subject_screening = self.get_subject_screening()
        subject_consent = self.get_subject_consent(subject_screening)
        self.assertIsNotNone(subject_consent.subject_identifier)

        subject_screening = self.get_subject_screening()
        subject_consent = self.get_subject_consent(subject_screening)
        self.assertIsNotNone(subject_consent.subject_identifier)

    def test_subjectconsent_form(self):

        subject_screening = self.get_subject_screening()
        data = dict(
            screening_identifier=subject_screening.screening_identifier,
            dob=subject_screening.report_datetime.date()
            - relativedelta(years=subject_screening.age_in_years),
            consent_datetime=get_now(),
            identity_type=MOBILE_NUMBER,
            identity="77777777",
            confirm_identity="77777777",
            gender=FEMALE,
            assessment_score=YES,
            consent_copy=YES,
            consent_reviewed=YES,
            consent_signature=YES,
            first_name="XAVIER",
            initials="XX",
            is_dob_estimated="-",
            is_incarcerated=NO,
            is_literate=YES,
            last_name="XAVIER",
            study_questions=YES,
            site=subject_screening.site,
            language="en",
            user_created="erikvw",
        )
        form = SubjectConsentForm(data=data, instance=None)
        form.is_valid()
        self.assertEqual(form._errors, {})
        form.save()
