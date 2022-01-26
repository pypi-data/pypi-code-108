from pprint import pprint

from django import forms
from django.test import TestCase
from edc_constants.constants import NOT_APPLICABLE, OTHER, STUDY_DEFINED_TIMEPOINT
from edc_form_validators import FormValidatorTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_schedule.constants import DAY1
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED

from mocca_lists.list_data import list_data
from mocca_lists.models import ClinicServices
from mocca_subject.choices import INFO_SOURCE
from mocca_subject.forms.subject_visit_form import SubjectVisitFormValidator

from ..mocca_test_case_mixin import MoccaTestCaseMixin


class TestSubjectVisit(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_screening = self.get_subject_screening(report_datetime=get_utcnow())
        self.subject_consent = self.get_subject_consent(
            subject_screening=self.subject_screening
        )

    def test_baseline_subject_visit_form(self):
        appointment = self.get_appointment(
            subject_identifier=self.subject_consent.subject_identifier,
            visit_code=DAY1,
            visit_code_sequence=0,
            reason=SCHEDULED,
        )
        clinic_services = ClinicServices.objects.filter(name=STUDY_DEFINED_TIMEPOINT)
        cleaned_data = dict(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            clinic_services=clinic_services,
            reason=SCHEDULED,
        )
        form_validator = SubjectVisitFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        pprint(form_validator._errors)
        self.assertNotIn("health_services", form_validator._errors)


class TestSubjectVisitFormValidator(MoccaTestCaseMixin, FormValidatorTestCaseMixin, TestCase):

    form_validator_default_form_cls = SubjectVisitFormValidator

    def setUp(self):
        super().setUp()
        self.subject_screening = self.get_subject_screening(report_datetime=get_utcnow())
        self.subject_consent = self.get_subject_consent(
            subject_screening=self.subject_screening
        )
        self.subject_visit = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
            visit_code=DAY1,
        )

    def test_form_validator_allows_missed_visit(self):
        cleaned_data = {
            "appointment": self.subject_visit.appointment,
            "report_datetime": self.subject_visit.report_datetime,
            "reason": MISSED_VISIT,
            "clinic_services": ClinicServices.objects.filter(name=NOT_APPLICABLE),
            "info_source": NOT_APPLICABLE,
        }
        form_validator = self.validate_form_validator(cleaned_data)
        self.assertDictEqual({}, form_validator._errors)

    def test_missed_visit_raises_validation_error_if_clinic_services_not_not_applicable(
        self,
    ):
        cleaned_data = {
            "appointment": self.subject_visit.appointment,
            "report_datetime": self.subject_visit.report_datetime,
            "reason": MISSED_VISIT,
            "info_source": NOT_APPLICABLE,
        }
        for value, _ in list_data["mocca_lists.clinicservices"]:
            if value != NOT_APPLICABLE:
                with self.subTest(value=value):
                    cleaned_data.update(
                        {
                            "clinic_services": ClinicServices.objects.filter(name=value),
                        }
                    )
                    if value == OTHER:
                        cleaned_data.update(
                            {"clinic_services_other": "some other clinic service"}
                        )
                    else:
                        cleaned_data.pop("clinic_services_other", None)

                    form_validator = self.validate_form_validator(cleaned_data)
                    self.assertIn("clinic_services", form_validator._errors)
                    self.assertIn(
                        (
                            "Expected 'Not applicable' response "
                            "(if this is a missed visit report)."
                        ),
                        str(form_validator._errors.get("clinic_services")),
                    )
                    self.assertEqual(len(form_validator._errors), 1, form_validator._errors)

    def test_missed_visit_raises_validation_error_if_info_source_not_not_applicable(
        self,
    ):
        cleaned_data = {
            "appointment": self.subject_visit.appointment,
            "report_datetime": self.subject_visit.report_datetime,
            "reason": MISSED_VISIT,
            "clinic_services": ClinicServices.objects.filter(name=NOT_APPLICABLE),
        }

        for value, _ in INFO_SOURCE:
            if value != NOT_APPLICABLE:
                with self.subTest(value=value):
                    cleaned_data.update({"info_source": value})
                    if value == OTHER:
                        cleaned_data.update(
                            {"info_source_other": "some other information source"}
                        )
                    else:
                        cleaned_data.pop("info_source_other", None)

                    form_validator = self.validate_form_validator(cleaned_data)
                    self.assertIn("info_source", form_validator._errors)
                    self.assertIn(
                        "This field is not applicable.",
                        str(form_validator._errors.get("info_source")),
                    )
                    self.assertEqual(len(form_validator._errors), 1, form_validator._errors)

    def test_missed_visit_raises_validation_error_if_multiple_clinic_services_selected(self):
        cleaned_data = {
            "appointment": self.subject_visit.appointment,
            "report_datetime": self.subject_visit.report_datetime,
            "reason": MISSED_VISIT,
            "clinic_services": ClinicServices.objects.filter().exclude(name=OTHER),
            "info_source": NOT_APPLICABLE,
        }
        form_validator = self.validate_form_validator(cleaned_data)
        self.assertIn("clinic_services", form_validator._errors)
        self.assertIn(
            "Invalid combination. 'Not applicable' may not be combined with other selections",
            str(form_validator._errors.get("clinic_services")),
        )
        self.assertEqual(len(form_validator._errors), 1, form_validator._errors)
