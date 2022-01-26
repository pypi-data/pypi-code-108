from typing import List

from django.test import TestCase
from edc_appointment.constants import INCOMPLETE_APPT
from edc_constants.constants import NO, NOT_APPLICABLE, POS, YES
from edc_metadata import KEYED, REQUIRED
from edc_metadata.models import CrfMetadata
from edc_utils import get_utcnow
from edc_visit_tracking.constants import UNSCHEDULED
from model_bakery import baker

from ..mocca_test_case_mixin import MoccaTestCaseMixin


class TestMetadataRules(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_screening = self.get_subject_screening(report_datetime=get_utcnow())
        self.subject_consent = self.get_subject_consent(
            subject_screening=self.subject_screening
        )

    @staticmethod
    def get_metadata_models(subject_visit) -> List[str]:
        crf_metadatas = CrfMetadata.objects.filter(
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            visit_code_sequence=subject_visit.visit_code_sequence,
        )
        return [
            obj.model
            for obj in crf_metadatas.filter(entry_status__in=[KEYED, REQUIRED]).order_by(
                "model"
            )
        ]

    def test_diagnoses_dates2(self):
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

        clinical_review = baker.make(
            "mocca_subject.clinicalreview",
            subject_visit=subject_visit,
            hiv_test=NOT_APPLICABLE,
            hiv_dx=NOT_APPLICABLE,
            hiv_test_date=None,
            htn_test=NO,
            htn_dx=NOT_APPLICABLE,
            htn_test_date=None,
            dm_test=NO,
            dm_dx=NOT_APPLICABLE,
            dm_test_date=None,
            chol_test=NO,
            chol_dx=NOT_APPLICABLE,
            chol_test_date=None,
        )

        models = self.get_metadata_models(subject_visit)
        self.assertIn("mocca_subject.hivreview", models)
        self.assertNotIn("mocca_subject.hivinitialreview", models)
        self.assertNotIn("mocca_subject.htninitialreview", models)
        self.assertNotIn("mocca_subject.dminitialreview", models)
        self.assertNotIn("mocca_subject.cholinitialreview", models)
        self.assertNotIn("mocca_subject.htnreview", models)
        self.assertNotIn("mocca_subject.dmreview", models)
        self.assertNotIn("mocca_subject.cholreview", models)

        clinical_review.htn_test = YES
        clinical_review.htn_test_date = subject_visit.report_datetime
        clinical_review.htn_dx = YES
        clinical_review.save()
        clinical_review.refresh_from_db()
        self.assertEqual(NOT_APPLICABLE, clinical_review.hiv_test)

        models = self.get_metadata_models(subject_visit)
        self.assertIn("mocca_subject.hivreview", models)
        self.assertIn("mocca_subject.htninitialreview", models)
        self.assertNotIn("mocca_subject.hivinitialreview", models)
        self.assertNotIn("mocca_subject.dminitialreview", models)
        self.assertNotIn("mocca_subject.htnreview", models)
        self.assertNotIn("mocca_subject.dmreview", models)
