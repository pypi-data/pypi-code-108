from django.test import TestCase, tag
from edc_appointment.constants import INCOMPLETE_APPT
from edc_constants.constants import INCOMPLETE, NO, NOT_APPLICABLE, YES
from edc_dx import Diagnoses
from edc_utils import get_utcnow
from edc_visit_tracking.constants import UNSCHEDULED
from model_bakery import baker

from mocca_screening.constants import HIV_CLINIC
from mocca_subject.forms import MedicationsForm

from ..mocca_test_case_mixin import MoccaTestCaseMixin


class TestMedications(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_screening = self.get_subject_screening(
            report_datetime=get_utcnow(), clinic_type=HIV_CLINIC
        )
        self.subject_consent = self.get_subject_consent(
            subject_screening=self.subject_screening, clinic_type=HIV_CLINIC
        )

        self.subject_visit_baseline = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )
        baker.make(
            "mocca_subject.clinicalreviewbaseline",
            subject_visit=self.subject_visit_baseline,
            hiv_test=YES,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )
        baker.make(
            "mocca_subject.hivinitialreview",
            subject_visit=self.subject_visit_baseline,
            dx_ago="5y",
            arv_initiation_ago="4y",
        )

    @tag("med")
    def test_refill_applicable_if_dx(self):
        Diagnoses(
            subject_identifier=self.subject_visit_baseline.subject_identifier,
            report_datetime=self.subject_visit_baseline.report_datetime,
            lte=True,
        )
        data = {
            "subject_visit": self.subject_visit_baseline,
            "report_datetime": self.subject_visit_baseline.report_datetime,
            "crf_status": INCOMPLETE,
            "refill_hiv": NOT_APPLICABLE,
            "refill_dm": NOT_APPLICABLE,
            "refill_htn": NOT_APPLICABLE,
        }
        form = MedicationsForm(data=data)
        form.is_valid()
        self.assertIn("refill_hiv", form._errors)
        data.update(refill_hiv=YES)
        form = MedicationsForm(data=data)
        form.is_valid()
        self.assertNotIn("refill_hiv", form._errors)

        self.subject_visit_baseline.appointment.appt_status = INCOMPLETE_APPT
        self.subject_visit_baseline.appointment.save()
        self.subject_visit_baseline.appointment.refresh_from_db()
        self.subject_visit_baseline.refresh_from_db()

        subject_visit = self.get_next_subject_visit(
            subject_visit=self.subject_visit_baseline, reason=UNSCHEDULED
        )

        baker.make(
            "mocca_subject.clinicalreview",
            subject_visit=subject_visit,
            hiv_test=NOT_APPLICABLE,
            hiv_dx=NOT_APPLICABLE,
            hiv_test_date=None,
        )

        data = {
            "subject_visit": subject_visit,
            "report_datetime": subject_visit.report_datetime,
            "crf_status": INCOMPLETE,
            "refill_hiv": NO,
            "refill_dm": NOT_APPLICABLE,
            "refill_htn": NOT_APPLICABLE,
        }

        form = MedicationsForm(data=data)
        form.is_valid()
        self.assertNotIn("refill_hiv", form._errors)

    @tag("med")
    def test_metadata_requires2(self):
        baker.make(
            "mocca_subject.medications",
            subject_visit=self.subject_visit_baseline,
        )
