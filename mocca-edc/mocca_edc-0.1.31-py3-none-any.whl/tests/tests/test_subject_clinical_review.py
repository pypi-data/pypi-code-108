from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_appointment.constants import INCOMPLETE_APPT
from edc_constants.constants import INCOMPLETE, NO, NOT_APPLICABLE, YES
from edc_utils import get_utcnow
from edc_visit_tracking.constants import UNSCHEDULED
from model_bakery import baker

from mocca_screening.constants import HIV_CLINIC
from mocca_subject.forms.clinical_review_form import ClinicalReviewForm

from ..mocca_test_case_mixin import MoccaTestCaseMixin


class TestClinicalReview(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_screening = self.get_subject_screening(
            report_datetime=get_utcnow(), clinic_type=HIV_CLINIC
        )
        self.subject_consent = self.get_subject_consent(
            subject_screening=self.subject_screening, clinic_type=HIV_CLINIC
        )

    @tag("cr")
    def test_clinical_review_requires_baseline_and_initial(self):
        subject_visit_baseline = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )
        subject_visit_baseline.appointment.appt_status = INCOMPLETE_APPT
        subject_visit_baseline.appointment.save()
        subject_visit_baseline.appointment.refresh_from_db()
        subject_visit_baseline.refresh_from_db()

        subject_visit = self.get_next_subject_visit(
            subject_visit=subject_visit_baseline, reason=UNSCHEDULED
        )

        data = {
            "subject_visit": subject_visit,
            "report_datetime": subject_visit.report_datetime,
            "crf_status": INCOMPLETE,
        }
        form = ClinicalReviewForm(data=data)
        form.is_valid()
        self.assertIn("__all__", form._errors)

        # add clinicalreviewbaseline
        baker.make(
            "mocca_subject.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            hiv_test=YES,
            hiv_test_date=get_utcnow() - relativedelta(years=5),
            hiv_dx=YES,
        )
        form = ClinicalReviewForm(data=data)
        form.is_valid()
        self.assertIn("__all__", form._errors)

        # add hivinitialreview
        baker.make(
            "mocca_subject.hivinitialreview",
            subject_visit=subject_visit_baseline,
            dx_date=get_utcnow() - relativedelta(years=5),
            arv_initiation_ago="4y",
        )

        form = ClinicalReviewForm(data=data)
        form.is_valid()
        self.assertNotIn("__all__", form._errors)

    @tag("cr")
    def test_hiv_na_if_diagnosed(self):
        subject_visit_baseline = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )
        baker.make(
            "mocca_subject.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )

        baker.make(
            "mocca_subject.hivinitialreview",
            subject_visit=subject_visit_baseline,
            dx_ago="5y",
            arv_initiation_ago="4y",
        )

        subject_visit_baseline.appointment.appt_status = INCOMPLETE_APPT
        subject_visit_baseline.appointment.save()
        subject_visit_baseline.appointment.refresh_from_db()
        subject_visit_baseline.refresh_from_db()

        subject_visit = self.get_next_subject_visit(
            subject_visit=subject_visit_baseline, reason=UNSCHEDULED
        )

        data = {
            "subject_visit": subject_visit,
            "report_datetime": subject_visit.report_datetime,
            "crf_status": INCOMPLETE,
        }
        for hiv_test in [YES, NO]:
            with self.subTest():
                data.update(hiv_test=hiv_test)
                form = ClinicalReviewForm(data=data)
                form.is_valid()
                self.assertIn("hiv_test", form._errors)
                self.assertIn("not applicable", form._errors.get("hiv_test")[0])

        data.update(hiv_test=NOT_APPLICABLE)
        form = ClinicalReviewForm(data=data)
        form.is_valid()
        self.assertNotIn("hiv_test", form._errors)
