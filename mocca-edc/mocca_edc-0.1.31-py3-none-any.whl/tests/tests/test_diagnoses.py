from django.test import TestCase
from edc_appointment.constants import INCOMPLETE_APPT
from edc_constants.constants import CHOL, DM, HIV, HTN, NOT_APPLICABLE, POS, YES
from edc_dx.diagnoses import (
    ClinicalReviewBaselineRequired,
    Diagnoses,
    InitialReviewRequired,
    MultipleInitialReviewsExist,
)
from edc_utils import get_utcnow
from edc_visit_tracking.constants import UNSCHEDULED
from model_bakery import baker

from mocca_screening.constants import HIV_CLINIC

from ..mocca_test_case_mixin import MoccaTestCaseMixin


class TestDiagnoses(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_screening = self.get_subject_screening(
            report_datetime=get_utcnow(), clinic_type=HIV_CLINIC
        )
        self.subject_consent = self.get_subject_consent(
            subject_screening=self.subject_screening, clinic_type=HIV_CLINIC
        )

    def test_diagnoses(self):
        subject_visit_baseline = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )

        subject_visit_baseline.save()

        self.assertRaises(
            ClinicalReviewBaselineRequired,
            Diagnoses,
            subject_identifier=subject_visit_baseline.subject_identifier,
        )

        clinical_review_baseline = baker.make(
            "mocca_subject.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            hiv_test=YES,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )
        try:
            diagnoses = Diagnoses(
                subject_identifier=subject_visit_baseline.subject_identifier,
            )
        except ClinicalReviewBaselineRequired:
            self.fail("DiagnosesError unexpectedly raised")

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertIsNone(diagnoses.get_dx(HTN))
        self.assertIsNone(diagnoses.get_dx(DM))

        clinical_review_baseline.htn_test = YES
        clinical_review_baseline.htn_test_ago = "1y"
        clinical_review_baseline.htn_dx = YES
        clinical_review_baseline.save()

        diagnoses = Diagnoses(
            subject_identifier=subject_visit_baseline.subject_identifier,
        )
        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertEqual(YES, diagnoses.get_dx(HTN))
        self.assertIsNone(diagnoses.get_dx(DM))

        clinical_review_baseline.dm_test = YES
        clinical_review_baseline.dm_test_ago = "1y"
        clinical_review_baseline.dm_dx = YES
        clinical_review_baseline.save()

        diagnoses = Diagnoses(
            subject_identifier=subject_visit_baseline.subject_identifier,
        )
        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertEqual(YES, diagnoses.get_dx(HTN))
        self.assertEqual(YES, diagnoses.get_dx(DM))

    def test_diagnoses_does_not_raise_for_subject_visit(self):
        """ "Note: Source of the exception will be in
        the metadata rule
        """
        try:
            subject_visit_baseline = self.get_subject_visit(
                subject_screening=self.subject_screening,
                subject_consent=self.subject_consent,
            )
        except ClinicalReviewBaselineRequired:
            self.fail("DiagnosesError unexpectedly raised")

        try:
            subject_visit_baseline.save()
        except ClinicalReviewBaselineRequired:
            self.fail("DiagnosesError unexpectedly raised")

    def test_diagnoses_dates_baseline_raises(self):
        subject_visit_baseline = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )

        baker.make(
            "mocca_subject.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            hiv_test=POS,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )

        diagnoses = Diagnoses(
            subject_identifier=subject_visit_baseline.subject_identifier,
        )
        self.assertRaises(InitialReviewRequired, getattr(diagnoses, "get_dx_date"), "hiv")

    def test_diagnoses_dates_baseline(self):
        subject_visit_baseline = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )

        clinical_review_baseline = baker.make(
            "mocca_subject.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            hiv_test=POS,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )
        baker.make(
            "mocca_subject.hivinitialreview",
            subject_visit=subject_visit_baseline,
            dx_ago="5y",
            arv_initiation_ago="4y",
        )
        diagnoses = Diagnoses(
            subject_identifier=subject_visit_baseline.subject_identifier,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertIsNone(diagnoses.get_dx(DM))
        self.assertIsNone(diagnoses.get_dx(HTN))
        self.assertIsNone(diagnoses.get_dx(CHOL))
        self.assertEqual(
            diagnoses.get_dx_date("hiv"),
            clinical_review_baseline.hiv_test_estimated_date,
        )
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))
        self.assertIsNone(diagnoses.get_dx_date(CHOL))

        diagnoses = Diagnoses(
            subject_identifier=subject_visit_baseline.subject_identifier,
            report_datetime=subject_visit_baseline.report_datetime,
            lte=True,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertIsNone(diagnoses.get_dx(DM))
        self.assertIsNone(diagnoses.get_dx(HTN))
        self.assertIsNone(diagnoses.get_dx(CHOL))
        self.assertEqual(
            diagnoses.get_dx_date(HIV),
            clinical_review_baseline.hiv_test_estimated_date,
        )
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))
        self.assertIsNone(diagnoses.get_dx_date(CHOL))

        diagnoses = Diagnoses(
            subject_identifier=subject_visit_baseline.subject_identifier,
            report_datetime=subject_visit_baseline.report_datetime,
            lte=False,
        )

        self.assertEqual(YES, diagnoses.get_dx(HIV))
        self.assertIsNone(diagnoses.get_dx(DM))
        self.assertIsNone(diagnoses.get_dx(HTN))
        self.assertIsNone(diagnoses.get_dx(CHOL))
        self.assertEqual(
            diagnoses.get_dx_date(HIV),
            clinical_review_baseline.hiv_test_estimated_date,
        )
        self.assertIsNone(diagnoses.get_dx_date(DM))
        self.assertIsNone(diagnoses.get_dx_date(HTN))
        self.assertIsNone(diagnoses.get_dx_date(CHOL))

    def test_diagnoses_dates(self):
        subject_visit_baseline = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )

        baker.make(
            "mocca_subject.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            hiv_test=POS,
            hiv_dx=YES,
            hiv_test_ago="5y",
        )

        hiv_initial_review = baker.make(
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

        baker.make(
            "mocca_subject.clinicalreview",
            subject_visit=subject_visit,
            hiv_test=NOT_APPLICABLE,
            hiv_dx=NOT_APPLICABLE,
            hiv_test_date=None,
            htn_test=YES,
            htn_dx=YES,
            htn_test_date=subject_visit.report_datetime,
        )

        htn_initial_review = baker.make(
            "mocca_subject.htninitialreview",
            subject_visit=subject_visit,
            dx_ago=None,
            dx_date=subject_visit.report_datetime,
        )

        diagnoses = Diagnoses(
            subject_identifier=subject_visit.subject_identifier,
            report_datetime=subject_visit.report_datetime,
            lte=True,
        )
        self.assertIsNotNone(diagnoses.get_dx_date("hiv"))
        self.assertEqual(
            diagnoses.get_dx_date("hiv"),
            hiv_initial_review.get_best_dx_date().date(),
        )

        self.assertEqual(
            diagnoses.get_dx_date("htn"),
            htn_initial_review.get_best_dx_date().date(),
        )
        self.assertIsNotNone(diagnoses.get_dx_date("htn"))

    def test_diagnoses_dates_baseline2(self):
        subject_visit_baseline = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
        )

        baker.make(
            "mocca_subject.clinicalreviewbaseline",
            subject_visit=subject_visit_baseline,
            hiv_test=POS,
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

        baker.make(
            "mocca_subject.hivinitialreview",
            subject_visit=subject_visit,
            dx_ago="5y",
            arv_initiation_ago="4y",
        )

        diagnoses = Diagnoses(
            subject_identifier=subject_visit_baseline.subject_identifier,
        )
        self.assertRaises(MultipleInitialReviewsExist, diagnoses.get_initial_reviews)
