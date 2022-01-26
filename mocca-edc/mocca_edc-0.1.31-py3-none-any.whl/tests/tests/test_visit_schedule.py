from django.test import TestCase, tag
from edc_utils import get_utcnow
from edc_visit_schedule.constants import DAY1
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED

from ..mocca_test_case_mixin import MoccaTestCaseMixin


class TestVisitSchedule(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.subject_screening = self.get_subject_screening(report_datetime=get_utcnow())
        self.subject_consent = self.get_subject_consent(
            subject_screening=self.subject_screening
        )

    def test_baseline(self):
        subject_visit = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
            visit_code=DAY1,
            reason=SCHEDULED,
        )
        self.assertEqual("1000", subject_visit.appointment.visit_code)
        self.assertEqual(0, subject_visit.appointment.visit_code_sequence)

    def test_next_up_to_12m(self):
        subject_visit = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
            visit_code=DAY1,
            reason=SCHEDULED,
        )

        for i in range(10, 130, 10):
            subject_visit = self.get_next_subject_visit(
                subject_visit=subject_visit,
                reason=SCHEDULED,
            )
            visit_code = str(1000 + i)
            self.assertEqual(visit_code, subject_visit.appointment.visit_code)
            self.assertEqual(0, subject_visit.appointment.visit_code_sequence)

    def test_next_unscheduled(self):
        subject_visit = self.get_subject_visit(
            subject_screening=self.subject_screening,
            subject_consent=self.subject_consent,
            visit_code=DAY1,
            reason=SCHEDULED,
        )

        subject_visit = self.get_next_subject_visit(
            subject_visit=subject_visit,
            reason=UNSCHEDULED,
        )
        self.assertEqual("1000", subject_visit.appointment.visit_code)
        self.assertEqual(1, subject_visit.appointment.visit_code_sequence)

        subject_visit = self.get_next_subject_visit(
            subject_visit=subject_visit,
            reason=UNSCHEDULED,
        )

        self.assertEqual("1000", subject_visit.appointment.visit_code)
        self.assertEqual(2, subject_visit.appointment.visit_code_sequence)

        subject_visit = self.get_next_subject_visit(
            subject_visit=subject_visit,
            reason=SCHEDULED,
        )

        self.assertEqual("1010", subject_visit.appointment.visit_code)
        self.assertEqual(0, subject_visit.appointment.visit_code_sequence)
