from django.test import TestCase, tag

from ..visit_schedules.schedule import schedule
from ..visit_schedules.visit_schedule import visit_schedule


class TestVisitSchedule(TestCase):
    def test_visit_schedule_models(self):
        self.assertEqual(visit_schedule.death_report_model, "mocca_ae.deathreport")
        self.assertEqual(visit_schedule.offstudy_model, "edc_offstudy.subjectoffstudy")
        self.assertEqual(visit_schedule.locator_model, "edc_locator.subjectlocator")

    def test_schedule_models(self):
        self.assertEqual(schedule.onschedule_model, "mocca_prn.onschedulehiv")
        self.assertEqual(schedule.offschedule_model, "mocca_prn.endofstudy")
        self.assertEqual(schedule.consent_model, "mocca_consent.subjectconsent")
        self.assertEqual(schedule.appointment_model, "edc_appointment.appointment")

    def test_crfs(self):
        prn = [
            "mocca_subject.bloodresultsfbc",
            "mocca_subject.bloodresultsglu",
            "mocca_subject.bloodresultshba1c",
            "mocca_subject.bloodresultslft",
            "mocca_subject.bloodresultsrft",
            "mocca_subject.urinedipsticktest",
        ]
        expected = {
            "1000": [
                "mocca_subject.physicalexam",
                "mocca_subject.patienthistory",
                "mocca_subject.bloodresultsfbc",
                "mocca_subject.bloodresultslft",
                "mocca_subject.bloodresultsrft",
                "mocca_subject.urinedipsticktest",
            ],
            "1005": [
                "mocca_subject.followupvitals",
                "mocca_subject.followup",
                "mocca_subject.clinicalreviewbaseline",
                "mocca_subject.medicationadherence",
            ],
            "1010": [
                "mocca_subject.followupvitals",
                "mocca_subject.followup",
                "mocca_subject.medicationadherence",
            ],
            "1030": [
                "mocca_subject.bloodresultslft",
                "mocca_subject.bloodresultsrft",
                "mocca_subject.followupvitals",
                "mocca_subject.followup",
                "mocca_subject.medicationadherence",
            ],
            "1060": [
                "mocca_subject.bloodresultshba1c",
                "mocca_subject.bloodresultslft",
                "mocca_subject.bloodresultsrft",
                "mocca_subject.followupvitals",
                "mocca_subject.followup",
                "mocca_subject.medicationadherence",
            ],
            "1090": [
                "mocca_subject.bloodresultslft",
                "mocca_subject.bloodresultsrft",
                "mocca_subject.followupvitals",
                "mocca_subject.followup",
                "mocca_subject.medicationadherence",
            ],
            "1120": [
                "mocca_subject.bloodresultsfbc",
                "mocca_subject.bloodresultsglu",
                "mocca_subject.bloodresultshba1c",
                "mocca_subject.bloodresultslft",
                "mocca_subject.bloodresultsrft",
                "mocca_subject.followupvitals",
                "mocca_subject.followup",
                "mocca_subject.medicationadherence",
                "mocca_subject.urinedipsticktest",
            ],
        }
        for visit_code, visit in schedule.visits.items():
            actual = [crf.model for crf in visit.crfs]
            actual.sort()
            expected.get(visit_code).sort()
            self.assertEqual(
                expected.get(visit_code), actual, msg=f"see CRFs for visit {visit_code}"
            )

            actual = [crf.model for crf in visit.crfs_prn]
            actual.sort()
            self.assertEqual(prn, actual, msg=f"see PRN CRFs for visit {visit_code}")
