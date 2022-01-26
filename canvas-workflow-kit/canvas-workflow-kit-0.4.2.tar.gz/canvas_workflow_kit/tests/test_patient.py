import io

from contextlib import redirect_stdout
from datetime import datetime, timedelta

import arrow

from canvas_workflow_kit.patient_recordset import BillingLineItemRecordSet, PatientRecordSet
from canvas_workflow_kit.tests.base import SDKBaseTest
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.v2018 import AnnualWellnessVisit, HomeHealthcareServices, OfficeVisit


class TestPatient(SDKBaseTest):

    def setUp(self):
        super().setUp()

    def test___init__(self):
        # no data
        tested = self.load_patient('empty')
        self.assertFalse(tested.active_only)
        self.assertEqual('empty', tested.patient_key)
        fields = [
            'billing_line_items',
            'conditions',
            'imaging_reports',
            'immunizations',
            'inpatient_stays',
            'instructions',
            'interviews',
            'lab_reports',
            'medications',
            'protocol_overrides',
            'referral_reports',
            'vital_signs',
            'suspect_hccs',
        ]
        for field in fields:
            self.assertTrue(hasattr(tested, field), 'patient misses the field %s' % field)
        # some data
        tested = self.load_patient('partial')
        self.assertFalse(tested.active_only)
        self.assertEqual('partial', tested.patient_key)

        fields = {
            'billing_line_items': 0,
            'conditions': 2,
            'imaging_reports': 1,
            'immunizations': 0,
            'inpatient_stays': 0,
            'instructions': 0,
            'interviews': 1,
            'lab_reports': 1,
            'medications': 1,
            'protocol_overrides': 0,
            'referral_reports': 0,
            'vital_signs': 2,
            'suspect_hccs': 0,
        }
        for field in fields:
            self.assertTrue(hasattr(tested, field), 'patient misses the field %s' % field)
            records = getattr(tested, field)
            self.assertEqual(fields[field], len(records),
                             '`%s` expected records %d' % (field, fields[field]))

        # # all data
        tested = self.load_patient('full')
        self.assertFalse(tested.active_only)
        self.assertEqual('full', tested.patient_key)
        fields = {
            'billing_line_items': 2,
            'conditions': 3,
            'imaging_reports': 2,
            'immunizations': 1,
            'inpatient_stays': 0,
            'instructions': 1,
            'interviews': 2,
            'lab_reports': 2,
            'medications': 2,
            'protocol_overrides': 2,
            'referral_reports': 1,
            'vital_signs': 3,
            'suspect_hccs': 0,
        }
        for field in fields:
            self.assertTrue(hasattr(tested, field), 'patient misses the field %s' % field)
            records = getattr(tested, field)
            self.assertEqual(fields[field], len(records),
                             '`%s` expected records %d' % (field, fields[field]))

    def test_recordset_classes(self):
        tested = self.load_patient('full')
        expected = [
            'AllergyIntoleranceRecordSet',
            'BillingLineItemRecordSet',
            'ConditionRecordSet',
            'ImagingReportRecordSet',
            'ImmunizationRecordSet',
            'InpatientStayRecordSet',
            'InstructionRecordSet',
            'InterviewRecordSet',
            'LabReportRecordSet',
            'MedicationRecordSet',
            'ProtocolOverrideRecordSet',
            'ReasonForVisitRecordSet',
            'ReferralRecordSet',
            'ReferralReportRecordSet',
            'UpcomingAppointmentNoteRecordSet',
            'UpcomingAppointmentRecordSet',
            'VitalSignRecordSet',
        ]
        count = 0
        for cls in tested.RECORDSET_CLASSES:
            self.assertTrue(issubclass(cls, PatientRecordSet), 'class %s' % cls.__name__)
            self.assertTrue(cls.__name__ in expected, 'class %s' % cls.__name__)
            count += 1
        self.assertEqual(len(expected), count)

    def test_recordset_fields(self):
        tested = self.load_patient('full')
        expected = [
            'allergy_intolerances',
            'billing_line_items',
            'conditions',
            'imaging_reports',
            'immunizations',
            'inpatient_stays',
            'instructions',
            'interviews',
            'lab_reports',
            'medications',
            'protocol_overrides',
            'reason_for_visits',
            'referrals',
            'referral_reports',
            'upcoming_appointment_notes',
            'upcoming_appointments',
            'vital_signs',
        ]
        self.assertEqual(expected, tested.recordset_fields())

    def test_first_name(self):
        tested = self.load_patient('empty')
        self.assertEqual('Jojo', tested.first_name)
        tested = self.load_patient('full')
        self.assertEqual('Darey', tested.first_name)
        tested = self.load_patient('partial')
        self.assertEqual('Toure', tested.first_name)

    def test_is_female(self):
        tested = self.load_patient('empty')
        self.assertFalse(tested.is_female)
        tested = self.load_patient('full')
        self.assertTrue(tested.is_female)
        tested = self.load_patient('partial')
        self.assertFalse(tested.is_female)

    def test_is_male(self):
        tested = self.load_patient('empty')
        self.assertFalse(tested.is_male)
        tested = self.load_patient('full')
        self.assertFalse(tested.is_male)
        tested = self.load_patient('partial')
        self.assertTrue(tested.is_male)

    def test_is_african_american(self):
        tested = self.load_patient('empty')
        self.assertFalse(tested.is_african_american)
        tested = self.load_patient('full')
        self.assertTrue(tested.is_african_american)
        tested = self.load_patient('partial')
        self.assertFalse(tested.is_african_american)

    def test_birthday(self):
        tested = self.load_patient('full')  # 1959-06-11
        self.assertIsInstance(tested.birthday, arrow.Arrow)
        self.assertEqual('1959-06-11', tested.birthday.format('YYYY-MM-DD'))

    def test_age(self):
        tested = self.load_patient('empty')
        expected = self.helper_age(1997, 7, 26)
        self.assertEqual(expected, tested.age)

        tested = self.load_patient('full')
        expected = self.helper_age(1959, 6, 11)
        self.assertEqual(expected, tested.age)

        tested = self.load_patient('partial')
        expected = self.helper_age(1974, 3, 24)
        self.assertEqual(expected, tested.age)

    def test_age_at(self):
        tested = self.load_patient('full')  # 1959-06-11

        self.assertAlmostEqual(
            49.997, tested.age_at(arrow.get('2009-06-10', 'YYYY-MM-DD')), places=3)
        self.assertAlmostEqual(
            50.000, tested.age_at(arrow.get('2009-06-11', 'YYYY-MM-DD')), places=3)
        self.assertAlmostEqual(
            50.003, tested.age_at(arrow.get('2009-06-12', 'YYYY-MM-DD')), places=3)
        self.assertAlmostEqual(
            50.501, tested.age_at(arrow.get('2009-12-11', 'YYYY-MM-DD')), places=3)

        # on leap year for date preceding the birthday and after the 02/29, the fraction is higher
        self.assertAlmostEqual(
            48.7213, tested.age_at(arrow.get('2008-03-01', 'YYYY-MM-DD')), places=4)
        self.assertAlmostEqual(
            49.7205, tested.age_at(arrow.get('2009-03-01', 'YYYY-MM-DD')), places=4)
        self.assertAlmostEqual(
            50.7205, tested.age_at(arrow.get('2010-03-01', 'YYYY-MM-DD')), places=4)
        self.assertAlmostEqual(
            51.7205, tested.age_at(arrow.get('2011-03-01', 'YYYY-MM-DD')), places=4)

        # on leap year for date following the birthday and befpre the 02/29, the fraction is lower
        self.assertAlmostEqual(
            49.2247, tested.age_at(arrow.get('2008-09-01', 'YYYY-MM-DD')), places=4)
        self.assertAlmostEqual(
            50.2247, tested.age_at(arrow.get('2009-09-01', 'YYYY-MM-DD')), places=4)
        self.assertAlmostEqual(
            51.2247, tested.age_at(arrow.get('2010-09-01', 'YYYY-MM-DD')), places=4)
        self.assertAlmostEqual(
            52.2240, tested.age_at(arrow.get('2011-09-01', 'YYYY-MM-DD')), places=4)

        # patient does NOT exist
        tested.patient = []
        self.assertEqual(0, tested.age_at(arrow.get('2011-09-01', 'YYYY-MM-DD')))

    def test_age_at_between(self):
        tested = self.load_patient('full')  # 1959-06-11
        self.assertTrue(tested.age_at_between(arrow.get('2009-06-10', 'YYYY-MM-DD'), 7, 50))
        self.assertFalse(tested.age_at_between(arrow.get('2009-06-10', 'YYYY-MM-DD'), 7, 49))

        self.assertTrue(tested.age_at_between(arrow.get('2009-06-11', 'YYYY-MM-DD'), 7, 51))
        self.assertFalse(tested.age_at_between(arrow.get('2009-06-11', 'YYYY-MM-DD'), 7, 50))

        self.assertTrue(tested.age_at_between(arrow.get('2009-06-12', 'YYYY-MM-DD'), 7, 51))
        self.assertFalse(tested.age_at_between(arrow.get('2009-06-12', 'YYYY-MM-DD'), 7, 50))

    def test_hospice_within(self):
        tested = self.load_patient('full')
        start = arrow.get('1999-06-10', 'YYYY-MM-DD')
        end = arrow.get('2109-06-10', 'YYYY-MM-DD')
        timeframe = Timeframe(start=start, end=end)
        self.assertFalse(tested.hospice_within(timeframe))

    def test_has_visit_within(self):
        tested = self.load_patient('full')
        start = arrow.get('2018-03-05', 'YYYY-MM-DD')
        end = arrow.get('2109-03-05', 'YYYY-MM-DD')
        timeframe = Timeframe(start=start, end=end)

        # no ValueSet provided --> True
        result = tested.has_visit_within(timeframe, None)
        self.assertTrue(result)

        tested.billing_line_items = BillingLineItemRecordSet([{
            'id': 92,
            'created': '2018-08-05T21:41:21.407046Z',
            'cpt': '99202',
            'units': 1
        }])
        # incorrect ValueSet + billing item --> False
        result = tested.has_visit_within(timeframe, AnnualWellnessVisit)
        self.assertFalse(result)
        # correct ValueSet + billing item + date within the time frame --> False
        result = tested.has_visit_within(timeframe, OfficeVisit)
        self.assertTrue(result)
        result = tested.has_visit_within(
            timeframe, AnnualWellnessVisit | OfficeVisit | HomeHealthcareServices)
        self.assertTrue(result)

        # date outside the time frame
        tested.billing_line_items = BillingLineItemRecordSet([{
            'id': 92,
            'created': '2018-02-05T21:41:21.407046Z',
            'cpt': '99202',
            'units': 1
        }])
        result = tested.has_visit_within(timeframe, OfficeVisit)
        self.assertFalse(result)

    def test_count_visit_within(self):
        tested = self.load_patient('full')
        start = arrow.get('2018-03-05', 'YYYY-MM-DD')
        end = arrow.get('2019-03-05', 'YYYY-MM-DD')
        timeframe = Timeframe(start=start, end=end)

        # no ValueSet provided --> True
        result = tested.count_visit_within(timeframe, None)
        self.assertEqual(0, result)

        tested.billing_line_items = BillingLineItemRecordSet([
            {'cpt': '99202', 'created': '2018-03-04T21:41:21.407046Z', },
            {'cpt': '99202', 'created': '2018-03-06T21:41:21.407046Z', },
            {'cpt': '99212', 'created': '2018-04-05T21:41:21.407046Z', },
            {'cpt': '99344', 'created': '2018-05-05T21:41:21.407046Z', },
            {'cpt': '99215', 'created': '2018-06-05T21:41:21.407046Z', },
            {'cpt': '99215', 'created': '2019-03-06T21:41:21.407046Z', },
        ])  # yapf: disable
        # incorrect ValueSet + billing item --> False
        result = tested.count_visit_within(timeframe, AnnualWellnessVisit)
        self.assertEqual(0, result)
        # correct ValueSet + billing item + date within the time frame --> False
        result = tested.count_visit_within(timeframe, OfficeVisit)
        self.assertEqual(3, result)
        result = tested.count_visit_within(
            timeframe, AnnualWellnessVisit | OfficeVisit | HomeHealthcareServices)
        self.assertEqual(4, result)

        # date outside the time frame
        tested.billing_line_items = BillingLineItemRecordSet([{
            'id': 92,
            'created': '2018-02-05T21:41:21.407046Z',
            'cpt': '99202',
            'units': 1
        }])
        result = tested.has_visit_within(timeframe, OfficeVisit)
        self.assertFalse(result)

    def test_as_dict(self):
        fields = [
            'allergy_intolerances',
            'billing_line_items',
            'conditions',
            'imaging_reports',
            'immunizations',
            'instructions',
            'interviews',
            'lab_reports',
            'medications',
            'protocol_overrides',
            'reason_for_visits',
            'referrals',
            'referral_reports',
            'upcoming_appointments',
            'upcoming_appointment_notes',
            'vital_signs',
        ]
        tested = self.load_patient('full')
        the_dict = tested.as_dict()

        self.assertTrue('patient_key' in the_dict)
        self.assertEqual('full', the_dict['patient_key'])
        self.assertTrue('patient' in the_dict)
        for field in fields:
            self.assertTrue(field in the_dict, 'patient.as_dict misses the field %s' % field)

    def test_print(self):
        tested = self.load_patient('full')
        f = io.StringIO()
        with redirect_stdout(f):
            tested.print()
        s = f.getvalue()
        self.assertGreater(len(s), 100)
        self.assertEqual('{\n  "patient_key": "full",\n', s[:27])

        # --- helpers

    def helper_age(self, year, month, day) -> float:
        bday = datetime(year=year, month=month, day=day)
        cday = datetime.today()
        age = 0
        if bday < cday:
            while bday.year < cday.year:
                age += 1
                bday = datetime(year=year + age, month=month, day=day)

            nominator = 0
            denominator = 0
            if bday < cday:
                nextyear = datetime(year=year + age + 1, month=month, day=day)
                while bday < nextyear:
                    bday += timedelta(days=1)
                    denominator += 1
                    if bday < cday:
                        nominator += 1
            else:
                age = age - 1
                nextyear = datetime(year=year + age, month=month, day=day)
                while nextyear < bday:
                    nextyear += timedelta(days=1)
                    denominator += 1
                    if nextyear < cday:
                        nominator += 1
            age += nominator / denominator

        return age
