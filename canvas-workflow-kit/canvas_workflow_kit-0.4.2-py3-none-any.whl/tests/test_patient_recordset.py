import arrow

from unittest import TestCase

from canvas_workflow_kit.patient_recordset import (
    BillingLineItemRecordSet,
    ConditionRecordSet,
    ImagingReportRecordSet,
    ImmunizationRecordSet,
    InstructionRecordSet,
    InterviewRecordSet,
    LabReportRecordSet,
    MedicationRecordSet,
    PatientEventRecordSet,
    PatientPeriodRecordSet,
    PatientRecordSet,
    ProtocolOverrideRecordSet,
    ReferralReportRecordSet,
    VitalSignRecordSet
)
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.value_set import ValueSet


class TestPatientRecordSet(TestCase):

    def test___init__(self):
        tested = self.get_object()
        result = tested.records
        expected = [
            190,
            194,
            193,
            192,
        ]

        self.assertEqual(len(expected), len(result))

        for exp, res in zip(expected, result):
            self.assertEqual(exp, res['id'])

        self.assertEqual(expected, [item['id'] for item in result])

        self.assertEqual('patient__key', PatientRecordSet.API_KEY_FIELD)
        self.assertIsNone(PatientRecordSet.API_UPDATE_FIELD)
        self.assertIsNone(PatientRecordSet.VALID_SYSTEMS)
        self.assertEqual('date', PatientRecordSet.DATE_FIELD)

    def test___str__(self):
        tested = self.get_object()
        result = str(tested)
        expected = '<UnitTestARecordSet: 4 records>'
        self.assertEqual(expected, result)

    def test___repr__(self):
        tested = self.get_object()
        result = repr(tested)
        expected = '<UnitTestARecordSet: 4 records>'
        self.assertEqual(expected, result)

    def test___iter__(self):
        tested = self.get_object()
        expected = [
            190,
            194,
            193,
            192,
        ]
        index = 0
        for itm in tested:
            self.assertEqual(expected[index], itm['id'])
            index += 1

    def test___getitem__(self):
        tested = self.get_object()
        expected = [
            190,
            194,
            193,
            192,
        ]
        for index in range(0, 2, 1):
            self.assertEqual(expected[index], tested[index]['id'])

    def test___bool__(self):
        # with records --> true
        tested = self.get_object()
        self.assertTrue(tested)
        # no record --> false
        tested = UnitTestARecordSet([])
        self.assertFalse(tested)

    def test___len__(self):
        # with records
        tested = self.get_object()
        self.assertEqual(4, len(tested))
        # no record
        tested = UnitTestARecordSet([])
        self.assertEqual(0, len(tested))

    def test___add__(self):
        tested = self.get_object()
        # different class
        other = UnitTestBRecordSet([{'id': 133}])
        with self.assertRaises(Exception):
            result = tested + other

        # same class
        other = UnitTestARecordSet([{'id': 133}])
        result = tested + other
        self.assertEqual(5, len(result))
        expected = [
            190,
            194,
            193,
            192,
            133,
        ]
        index = 0
        for itm in result:
            self.assertEqual(expected[index], itm['id'])
            index += 1

    def test_new_from(self):
        records = [
            {
                'id': 190,
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34560'
                    }]
                }
            },
            {
                'id': 191,
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34561'
                    }]
                }
            },
        ]  # yapf: disable

        tested = UnitTestARecordSet([])
        self.assertEqual(0, len(tested))

        result = tested.new_from(records)
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(2, len(result))
        ids = [
            190,
            191,
        ]
        self.assertEqual(ids, [item['id'] for item in result])

    def test_item_to_codes(self):
        tests = [{
            'exp': [],
            'itm': {
                'codes': {
                    'coding': [{
                        'id': 111,
                        'system': 'ICD-10',
                    }]
                },
                'codings': [{
                    'id': 123,
                    'system': 'ICD-10',
                }]
            }
        }, {
            'exp': [{
                'id': 111,
                'system': 'ICD-10',
            }],
            'itm': {
                'code': {
                    'coding': [{
                        'id': 111,
                        'system': 'ICD-10',
                    }]
                },
                'coding': [{
                    'id': 123,
                    'system': 'ICD-10',
                }]
            }
        }, {
            'exp': [{
                'id': 123,
                'system': 'ICD-10',
            }],
            'itm': {
                'cod': {
                    'coding': [{
                        'id': 111,
                        'system': 'ICD-10',
                    }]
                },
                'coding': [{
                    'id': 123,
                    'system': 'ICD-10',
                }]
            }
        }]  # yapf: disable
        for test in tests:
            expected = test['exp']
            result = PatientRecordSet.item_to_codes(test['itm'])
            self.assertEqual(expected, result)

    def test_validated(self):
        # no record with committer --> no record
        tested = self.get_object()
        result = tested.validated()
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(0, len(result))

        # record with committer
        tested += UnitTestARecordSet([
            {
                'id': 231,
                'committer': None
            },
            {
                'id': 232,
                'committer': 3,
                'deleted': False
            },
            {
                'id': 233,
                'committer': 3,
                'deleted': True
            },
            {
                'id': 234,
                'committer': 3
            },
            {
                'id': 235,
                'committer': 3,
                'enteredInError': None
            },
            {
                'id': 236,
                'committer': 3,
                'enteredInError': 5
            },
            {
                'id': 237,
                'committer': 3,
                'entered_in_error': None
            },
            {
                'id': 238,
                'committer': 3,
                'entered_in_error': 7
            },
        ])
        result = tested.validated()
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(4, len(result))
        self.assertEqual([232, 234, 235, 237], [p['id'] for p in result])

    def test__enumerate_system_list_codes(self):

        class UnitTestReco(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Reco for the unit tests'
            CPT = {'abc', '123'}
            SNOMEDCT = {'12345', '23456', '34561', '34562', '34563', '34564'}

        tested = self.get_object()
        expected = {
            'id': [
                190,
                194,
                192,
                193,
            ],
            'coding': [
                {
                    'system': 'http://snomed.info/sct',
                    'code': '34561',
                },
                {
                    'system': 'http://snomed.info/sct',
                    'code': '34562',
                },
                {
                    'system': 'http://snomed.info/sct',
                    'code': '34563',
                },
                {
                    'system': 'http://snomed.info/sct',
                    'code': '34564',
                },
            ]
        }
        count = 0
        for item, code, list_codes in tested._enumerate_system_list_codes(UnitTestReco):
            count = count + 1
            self.assertIn(item['id'], expected['id'])
            self.assertIn(code, expected['coding'])
            self.assertEqual({'12345', '34561', '34563', '34564', '23456', '34562'}, list_codes)
        self.assertEqual(4, count)

    def test_filter(self):
        tested = self.get_object()

        # Test simple filter of ids
        self.assertEqual(1, len(tested.filter(id=193)))
        self.assertEqual(2, len(tested.filter(id__lt=193)))
        self.assertEqual(3, len(tested.filter(id__lte=193)))
        self.assertEqual(2, len(tested.filter(id__gte=193)))
        self.assertEqual(1, len(tested.filter(id__gt=193)))

        # Test nested filter
        self.assertEqual(tested.filter(nested__id=1)[0]['id'], 192)
        self.assertEqual(len(tested.filter(nested__timestamp__gte=arrow.get("2021-01-01"))), 1)

    def test_find(self):

        class UnitTestReco(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Reco for the unit tests'
            CPT = {'abc', '123'}
            SNOMEDCT = {'12345', '23456', '34567'}

        # no valid system --> error
        tested = UnitTestNoSystemRecordSet([])
        with self.assertRaises(Exception):
            tested.find(UnitTestReco)

        # valid system
        # - no record with code / coding
        tested = self.get_object()
        result = tested.find(UnitTestReco)
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(0, len(result))

        # - record with code / coding + no valid system
        tested += UnitTestARecordSet([{
            'id': 190,
            'code': {
                'coding': [{
                    'id': 101,
                    'system': 'ICD-10',
                    'code': '34561'
                }]
            }
        }])
        result = tested.find(UnitTestReco)
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(0, len(result))

        # - record with code / coding + valid system + no valid code
        tested += UnitTestARecordSet([{
            'id': 191,
            'code': {
                'coding': [{
                    'id': 111,
                    'system': 'http://snomed.info/sct',
                    'code': '11111'
                }]
            }
        }])
        result = tested.find(UnitTestReco)
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(0, len(result))

        # - record with code / coding + invalid system + valid code
        tested += UnitTestARecordSet([{
            'id': 192,
            'code': {
                'coding': [{
                    'id': 121,
                    'system': 'NOPE',
                    'code': '34567'
                }]
            }
        }])
        result = tested.find(UnitTestReco)
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(0, len(result))

        # - record with code / coding + valid system + valid code
        tested += UnitTestARecordSet([{
            'id': 192,
            'code': {
                'coding': [{
                    'id': 121,
                    'system': 'http://snomed.info/sct',
                    'code': '34567'
                }]
            }
        }])
        result = tested.find(UnitTestReco)
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(1, len(result))

        # - record with code / coding + valid system + valid code
        tested += UnitTestARecordSet([{
            'id': 193,
            'code': {
                'coding': [{
                    'id': 122,
                    'system': 'http://snomed.info/sct',
                    'code': '34567'
                }]
            }
        }])
        result = tested.find(UnitTestReco)
        self.assertIsInstance(result, UnitTestARecordSet)
        self.assertEqual(2, len(result))
        expected = [192, 193]
        for rec in result:
            exp_id = expected.pop(0)
            self.assertEqual(exp_id, rec['id'])

    def test_find_class(self):

        class UnitTestReco(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Reco for the unit tests'
            CPT = {'abc', '123'}
            SNOMEDCT = {r'123\d*', r'[A-Z]{2}\d{2}', '34567'}

        tests = [
            '34567',
            '12345',
            'GO67',
            'GO6745',
        ]
        for code in tests:
            # no valid system --> error
            tested = UnitTestNoSystemRecordSet([])
            with self.assertRaises(Exception):
                tested.find_class(UnitTestReco)

            # valid system
            # - no record with code / coding
            tested = self.get_object()
            result = tested.find_class(UnitTestReco)
            self.assertIsInstance(result, UnitTestARecordSet)
            self.assertEqual(0, len(result))

            # - record with code / coding + no valid system
            tested += UnitTestARecordSet([{
                'id': 190,
                'code': {
                    'coding': [{
                        'id': 101,
                        'system': 'ICD-10',
                        'code': code
                    }]
                }
            }])
            result = tested.find_class(UnitTestReco)
            self.assertIsInstance(result, UnitTestARecordSet)
            self.assertEqual(0, len(result))

            # - record with code / coding + valid system + no valid code
            tested += UnitTestARecordSet([{
                'id': 191,
                'code': {
                    'coding': [{
                        'id': 111,
                        'system': 'http://snomed.info/sct',
                        'code': '11111'
                    }]
                }
            }])
            result = tested.find_class(UnitTestReco)
            self.assertIsInstance(result, UnitTestARecordSet)
            self.assertEqual(0, len(result))

            # - record with code / coding + invalid system + valid code
            tested += UnitTestARecordSet([{
                'id': 192,
                'code': {
                    'coding': [{
                        'id': 121,
                        'system': 'NOPE',
                        'code': code
                    }]
                }
            }])
            result = tested.find_class(UnitTestReco)
            self.assertIsInstance(result, UnitTestARecordSet)
            self.assertEqual(0, len(result))

            # - record with code / coding + valid system + valid code
            tested += UnitTestARecordSet([{
                'id': 192,
                'code': {
                    'coding': [{
                        'id': 121,
                        'system': 'http://snomed.info/sct',
                        'code': code
                    }]
                }
            }])
            result = tested.find_class(UnitTestReco)
            self.assertIsInstance(result, UnitTestARecordSet)
            self.assertEqual(1, len(result))

            # - record with code / coding + valid system + valid code
            tested += UnitTestARecordSet([{
                'id': 193,
                'code': {
                    'coding': [{
                        'id': 122,
                        'system': 'http://snomed.info/sct',
                        'code': code
                    }]
                }
            }])
            result = tested.find_class(UnitTestReco)
            self.assertIsInstance(result, UnitTestARecordSet)
            self.assertEqual(2, len(result))
            expected = [192, 193]
            for rec in result:
                exp_id = expected.pop(0)
                self.assertEqual(exp_id, rec['id'])

    # --- helper ----
    def get_object(self):
        self.assertTrue(issubclass(UnitTestARecordSet, PatientRecordSet))
        records = [
            {
                'id': 190,
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34561'
                    }]
                }
            },
            {
                'id': 194,
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34564'
                    }]
                }
            },
            {
                'id': 193,
                'nested': {
                    'id': 2,
                    'timestamp': '2020-01-01T15:41:14.597558Z'
                },
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34563'
                    }]
                }
            },
            {
                'id': 192,
                'nested': {
                    'id': 1,
                    'timestamp': '2021-08-11T15:41:14.597558Z'
                },
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34562'
                    }]
                }
            },
        ]
        return UnitTestARecordSet(records)


class TestPatientRecordSetEvent(TestCase):

    def test___init__(self):
        tested = self.get_object()
        result = tested.records
        expected = [
            138,
            123,
            456,
        ]
        self.assertEqual(len(expected), len(result))
        for exp, res in zip(expected, result):
            self.assertEqual(exp, res['id'])

        self.assertEqual(expected, [item['id'] for item in result])

    def test_filter_function(self):

        def filter_fn(an_arrow: arrow.Arrow) -> bool:
            return an_arrow.datetime.hour == 13

        # date field empty
        records = [
            {
                'id': 190,
                'fldDate': '',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 191,
                'fldDate': '',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 192,
                'fldDate': '',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 193,
                'fldDate': '',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
        ]
        tested = UnitTestRecordSetEvent(records)
        result = tested.filter_function(filter_fn)
        self.assertEqual(0, len(result))

        # date field present
        tested = self.get_object_with_data()
        result = tested.filter_function(filter_fn)
        self.assertEqual(2, len(result))
        expected = [190, 192]
        for rec in result:
            exp_id = expected.pop(0)
            self.assertEqual(exp_id, rec['id'])

    def test_within(self):
        tested = self.get_object_with_data()
        fmt = 'YYYY-MM-DD HH:mm:ss'
        tests = [
            [
                arrow.get('2018-08-20 13:32:00', fmt),
                arrow.get('2018-08-20 14:33:00', fmt), [192, 193]
            ],
            [arrow.get('2018-08-20 13:32:45', fmt),
             arrow.get('2018-08-20 13:32:45', fmt), [192]],
            [arrow.get('2018-08-20 13:32:00', fmt),
             arrow.get('2018-08-20 13:32:44', fmt), []],
        ]
        for (start, end, expected) in tests:
            tfr = Timeframe(start, end)
            result = tested.within(tfr)
            self.assertEqual(len(expected), len(result))
            for rec in result:
                exp_id = expected.pop(0)
                self.assertEqual(exp_id, rec['id'])

    def test_before(self):
        tested = self.get_object_with_data()

        fmt = 'YYYY-MM-DD HH:mm:ss'
        tests = [
            [arrow.get('2018-08-20 13:33:33', fmt), [190, 191, 192]],
            [arrow.get('2018-08-19 13:32:45', fmt), [190]],
            [arrow.get('2018-08-19 13:32:44', fmt), []],
        ]
        for (end, expected) in tests:
            result = tested.before(end)
            self.assertEqual(len(expected), len(result))
            for rec in result:
                exp_id = expected.pop(0)
                self.assertEqual(exp_id, rec['id'])

    def test_after(self):
        tested = self.get_object_with_data()

        fmt = 'YYYY-MM-DD HH:mm:ss'
        tests = [
            [arrow.get('2018-08-20 12:32:00', fmt), [191, 192, 193]],
            [arrow.get('2018-08-20 13:32:45', fmt), [192, 193]],
            [arrow.get('2018-08-20 14:32:45', fmt), [193]],
            [arrow.get('2018-08-20 14:32:46', fmt), []],
        ]
        for (start, expected) in tests:
            result = tested.after(start)
            self.assertEqual(len(expected), len(result))
            for rec in result:
                exp_id = expected.pop(0)
                self.assertEqual(exp_id, rec['id'])

    def test_within_one_year(self):
        tested = self.get_object_per_year()
        fmt = 'YYYY-MM-DD HH:mm:ss'
        tests = [
            [
                arrow.get('2000-08-20 13:32:00', fmt),
                arrow.get('2019-03-20 13:32:44', fmt), [191, 192]
            ],
            [arrow.get('2000-08-20 13:32:00', fmt),
             arrow.get('2020-03-20 13:32:45', fmt), [193]],
            [arrow.get('2000-08-20 13:32:00', fmt),
             arrow.get('2020-03-20 13:32:46', fmt), []],
        ]
        for (start, end, expected) in tests:
            tfr = Timeframe(start, end)
            result = tested.within_one_year(tfr)
            self.assertEqual(len(expected), len(result))
            for rec in result:
                exp_id = expected.pop(0)
                self.assertEqual(exp_id, rec['id'])

    def test_within_two_years(self):
        tested = self.get_object_per_year()
        fmt = 'YYYY-MM-DD HH:mm:ss'
        tests = [
            [
                arrow.get('2000-08-20 13:32:00', fmt),
                arrow.get('2019-03-20 13:32:44', fmt), [190, 191, 192]
            ],
            [
                arrow.get('2000-08-20 13:32:00', fmt),
                arrow.get('2020-03-20 13:32:44', fmt), [191, 192, 193]
            ],
            [arrow.get('2000-08-20 13:32:00', fmt),
             arrow.get('2021-03-20 13:32:45', fmt), [193]],
            [arrow.get('2000-08-20 13:32:00', fmt),
             arrow.get('2022-03-20 13:32:46', fmt), []],
        ]
        for (start, end, expected) in tests:
            tfr = Timeframe(start, end)
            result = tested.within_two_years(tfr)
            self.assertEqual(len(expected), len(result))
            for rec in result:
                exp_id = expected.pop(0)
                self.assertEqual(exp_id, rec['id'])

    def test_first(self):
        # no record
        tested = UnitTestRecordSetEvent([])
        self.assertIsNone(tested.first())
        # with record
        tested = self.get_object()
        result = tested.first()
        self.assertEqual(138, result['id'])

    def test_last(self):
        # no record
        tested = UnitTestRecordSetEvent([])
        self.assertIsNone(tested.last())
        # with record
        tested = self.get_object()
        result = tested.last()
        self.assertEqual(456, result['id'])

    def test_last_value(self):
        # no record
        tested = UnitTestRecordSetEvent([])
        self.assertIsNone(tested.last_value())
        # with record without casting
        tested = self.get_object()
        result = tested.last_value()
        self.assertEqual('133.55', result)
        # with record with casting
        tested = self.get_object()
        result = tested.last_value(float)
        self.assertEqual(133.55, result)
        # incorrect casting
        result = tested.last_value(int)
        self.assertIsNone(result)

    # --- helpers
    def get_object(self):
        self.assertTrue(issubclass(UnitTestRecordSetEvent, PatientEventRecordSet))
        records = [
            {
                'id': 123,
                'fldDate': '2018-08-19 12:32:45',
                'value': '123AB'
            },
            {
                'id': 456,
                'fldDate': '2018-08-19 12:32:59',
                'value': '133.55'
            },
            {
                'id': 459,
                'fldDate': None
            },
            {
                'id': 138,
                'fldDate': '2018-08-19 10:32:45',
                'value': '143AB'
            },
        ]
        return UnitTestRecordSetEvent(records)

    def get_object_with_data(self):
        self.assertTrue(issubclass(UnitTestRecordSetEvent, PatientEventRecordSet))
        records = [
            {
                'id': 190,
                'fldDate': '2018-08-19 13:32:45',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 191,
                'fldDate': '2018-08-20 12:32:45',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 192,
                'fldDate': '2018-08-20 13:32:45',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 193,
                'fldDate': '2018-08-20 14:32:45',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
        ]
        return UnitTestRecordSetEvent(records)

    def get_object_per_year(self):
        self.assertTrue(issubclass(UnitTestRecordSetEvent, PatientRecordSet))
        records = [
            {
                'id': 190,
                'fldDate': '2018-03-19 13:32:45',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 191,
                'fldDate': '2018-07-20 13:32:45',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 192,
                'fldDate': '2018-11-20 13:32:45',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
            {
                'id': 193,
                'fldDate': '2019-03-20 13:32:45',
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34567'
                    }]
                }
            },
        ]
        return UnitTestRecordSetEvent(records)


class TestPatientRecordSetPeriod(TestCase):

    def test___init__(self):
        tested = self.get_object()
        result = tested.records
        expected = [
            190,
            194,
            192,
        ]
        self.assertEqual(len(expected), len(result))
        for exp, res in zip(expected, result):
            self.assertEqual(exp, res['id'])

        self.assertEqual(expected, [item['id'] for item in result])

    def test_intersects(self):
        tested = self.get_object()

        timeframe = Timeframe(start=arrow.get('2018-07-15'), end=arrow.get('2018-08-02'))
        result = tested.intersects(timeframe, still_active=False)
        expected = []
        self.assertEqual(expected, [item['id'] for item in result])

        timeframe = Timeframe(start=arrow.get('2018-07-15'), end=arrow.get('2018-08-20'))
        result = tested.intersects(timeframe, still_active=False)
        expected = [
            190,
            194,
        ]
        self.assertEqual(expected, [item['id'] for item in result])

        timeframe = Timeframe(start=arrow.get('2018-07-15'), end=arrow.get('2018-12-20'))
        result = tested.intersects(timeframe, still_active=False)
        expected = [
            190,
            194,
            192,
        ]
        self.assertEqual(expected, [item['id'] for item in result])

        timeframe = Timeframe(start=arrow.get('2018-10-15'), end=arrow.get('2018-11-20'))
        result = tested.intersects(timeframe, still_active=False)
        expected = [
            190,
            194,
        ]
        self.assertEqual(expected, [item['id'] for item in result])

        timeframe = Timeframe(start=arrow.get('2018-12-15'), end=arrow.get('2018-12-20'))
        result = tested.intersects(timeframe, still_active=False)
        expected = [
            190,
            192,
        ]
        self.assertEqual(expected, [item['id'] for item in result])

        timeframe = Timeframe(start=arrow.get('2018-09-05'), end=arrow.get('2018-11-15'))
        result = tested.intersects(timeframe, still_active=False)
        expected = [
            190,
            194,
        ]
        self.assertEqual(expected, [item['id'] for item in result])
        result = tested.intersects(timeframe, still_active=True)
        expected = [
            190,
        ]
        self.assertEqual(expected, [item['id'] for item in result])

        timeframe = Timeframe(start=arrow.get('2018-09-05'), end=arrow.get('2018-11-05'))
        result = tested.intersects(timeframe, still_active=False)
        expected = [
            190,
            194,
        ]
        self.assertEqual(expected, [item['id'] for item in result])
        result = tested.intersects(timeframe, still_active=True)
        expected = [
            190,
            194,
        ]
        self.assertEqual(expected, [item['id'] for item in result])

    def test_starts_before(self):
        tested = self.get_object()

        result = tested.starts_before(arrow.get('2018-07-15'))
        expected = []
        self.assertEqual(expected, [item['id'] for item in result])

        result = tested.starts_before(arrow.get('2018-09-15'))
        expected = [
            190,
        ]
        self.assertEqual(expected, [item['id'] for item in result])

        result = tested.starts_before(arrow.get('2018-12-15'))
        expected = [
            190,
            192,
        ]
        self.assertEqual(expected, [item['id'] for item in result])

    # --- helper ----
    def get_object(self):
        self.assertTrue(issubclass(UnitTestRecordSetPeriod, PatientPeriodRecordSet))
        records = [
            {
                'id': 190,
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34561'
                    }]
                },
                'periods': [
                    {
                        'from': '2018-08-15',
                        'to': '2018-08-25'
                    },
                    {
                        'from': '2018-09-05',
                        'to': None
                    },
                ]
            },
            {
                'id': 194,
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34564'
                    }]
                },
                'periods': [
                    {
                        'from': '2018-08-15',
                        'to': '2018-08-25'
                    },
                    {
                        'from': '2018-09-10',
                        'to': '2018-11-10'
                    },
                ]
            },
            {
                'id': 193,
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34563'
                    }]
                },
                'periods': []
            },
            {
                'id': 192,
                'code': {
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': '34562'
                    }]
                },
                'periods': [{
                    'from': '2018-11-30',
                    'to': None
                }]
            },
        ]
        return UnitTestRecordSetPeriod(records)


class TestBillingLineItemRecordSet(TestCase):

    def test_constants(self):
        tested = BillingLineItemRecordSet([])
        self.assertIsInstance(tested, BillingLineItemRecordSet)
        self.assertEqual(['cpt', 'hcpcs'], tested.VALID_SYSTEMS)
        self.assertEqual('created', tested.DATE_FIELD)
        self.assertEqual('billing_line_items', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('billingLineItems', tested.API_UPDATE_FIELD)


class TestConditionRecordSet(TestCase):

    def test_constants(self):
        tested = ConditionRecordSet([])
        self.assertIsInstance(tested, PatientPeriodRecordSet)
        self.assertEqual(['icd10cm', 'icd10pcs', 'snomedct'], tested.VALID_SYSTEMS)
        self.assertEqual('conditions', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('conditions', tested.API_UPDATE_FIELD)

    def test_item_to_codes(self):
        tested = ConditionRecordSet
        tests = [
            ('active', True),
            ('remission', False),
            ('relapse', False),
            ('resolved', True),
            ('investigative', False),
        ]
        for status, expected in tests:
            item = {
                'clinicalStatus': status,
                'coding': [{
                    'system': 'ICD-10',
                    'code': 'I420'
                }],
                'periods': [{
                    'from': '2018-08-23',
                    'to': None
                }],
            }
            result = tested.item_to_codes(item)
            if expected:
                self.assertEqual(item['coding'], result)
            else:
                self.assertEqual([], result)


class TestImmunizationRecordSet(TestCase):

    def test_constants(self):
        tested = ImmunizationRecordSet([])
        self.assertIsInstance(tested, PatientEventRecordSet)
        self.assertEqual(['cvx'], tested.VALID_SYSTEMS)
        self.assertEqual('dateOrdered', tested.DATE_FIELD)
        self.assertEqual('immunizations', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('immunizations', tested.API_UPDATE_FIELD)

    def test_item_to_codes(self):
        item = {
            'codes': {
                'value': '124AB'
            },
            'code': {
                'value': '456AB'
            },
            'coding': {
                'value': '123AB'
            },
            'codings': {
                'value': '789AB'
            },
        }
        self.assertEqual({'value': '123AB'}, ImmunizationRecordSet.item_to_codes(item))


class TestVitalSignRecordSet(TestCase):

    def test_constants(self):
        tested = VitalSignRecordSet([])
        self.assertIsInstance(tested, PatientEventRecordSet)
        self.assertEqual(['loinc'], tested.VALID_SYSTEMS)
        self.assertEqual('dateRecorded', tested.DATE_FIELD)
        self.assertEqual('vital_signs', tested.PATIENT_FIELD)
        self.assertEqual('reading__patient__key', tested.API_KEY_FIELD)
        self.assertEqual('vitalSigns', tested.API_UPDATE_FIELD)

    def test_item_to_codes(self):
        item = {
            'loinxNum': '29463-4',
            'loincNum': '29463-5',
            'loincNux': '29463-6',
        }
        self.assertEqual([{
            'code': '29463-5',
            'system': 'http://loinc.org'
        }], VitalSignRecordSet.item_to_codes(item))


class TestLabReportRecordSet(TestCase):

    def test_constants(self):
        tested = LabReportRecordSet([])
        self.assertIsInstance(tested, PatientEventRecordSet)
        self.assertEqual(['loinc'], tested.VALID_SYSTEMS)
        self.assertEqual('originalDate', tested.DATE_FIELD)
        self.assertEqual('lab_reports', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('labReports', tested.API_UPDATE_FIELD)

    def test_item_to_codes(self):
        item = {
            'loincCodex': [{
                'id': 21,
                'code': '1798-',
                'name': 'Amylasey',
            }],
            'loincCodes': [
                {
                    'id': 38,
                    'code': '1798-8',
                    'name': 'Amylase',
                },
                {
                    'id': 37,
                    'code': '1798-3',
                    'name': 'Amylasx',
                },
                {
                    'id': 39,
                    'code': '1798-',
                    'name': 'Amylasey',
                },
            ],
            'loincCodey': [{
                'id': 32,
                'code': '1798-8',
                'name': 'Amylase',
            }],
        }
        expected = [{
            'system': 'http://loinc.org',
            'id': 38,
            'code': '1798-8',
            'name': 'Amylase',
        }, {
            'system': 'http://loinc.org',
            'id': 37,
            'code': '1798-3',
            'name': 'Amylasx',
        }, {
            'system': 'http://loinc.org',
            'id': 39,
            'code': '1798-',
            'name': 'Amylasey',
        }]
        self.assertEqual(expected, LabReportRecordSet.item_to_codes(item))

    def test_new_from(self):
        records = [{
            'test': 123,
            'values': [
                {
                    'originalDate': '2018-05-29',
                    'id': 911,
                    'loincCodes': [{
                        'id': 38,
                        'created': '2018-05-29T02:38:22.011169Z',
                        'code': '1798-8',
                    }]
                },
                {
                    'originalDate': '2018-05-29',
                    'id': 912,
                    'loincCodes': [{
                        'id': 47,
                        'created': '2018-05-30T02:38:22.011169Z',
                        'code': '1798-8',
                    }]
                },
            ],
            'originalDate': '2018-05-29'
        }]
        tested = LabReportRecordSet([])
        self.assertEqual(0, len(tested.records))

        result = tested.new_from(records)
        self.assertIsInstance(result, LabReportRecordSet)
        self.assertNotEqual(tested, result)

        self.assertEqual(2, len(result))
        expected = [{
            'originalDate': '2018-05-29',
            'id': 911,
            'loincCodes': [{
                'id': 38,
                'created': '2018-05-29T02:38:22.011169Z',
                'code': '1798-8'
            }]
        }, {
            'originalDate': '2018-05-29',
            'id': 912,
            'loincCodes': [{
                'id': 47,
                'created': '2018-05-30T02:38:22.011169Z',
                'code': '1798-8'
            }]
        }]  # yapf: disable
        for exp_item, res_item in zip(expected, result):
            self.assertEqual(exp_item['id'], res_item['id'])


class TestInstructionRecordSet(TestCase):

    def test_constants(self):
        tested = InstructionRecordSet([])
        self.assertIsInstance(tested, PatientEventRecordSet)
        self.assertEqual(['icd10cm', 'icd10pcs', 'snomedct', 'cpt', 'hcpcs'], tested.VALID_SYSTEMS)
        self.assertEqual('noteTimestamp', tested.DATE_FIELD)
        self.assertEqual('instructions', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('instructions', tested.API_UPDATE_FIELD)


class TestMedicationRecordSet(TestCase):

    def test_constants(self):
        tested = MedicationRecordSet([])
        self.assertIsInstance(tested, PatientPeriodRecordSet)
        self.assertEqual([
            'rxnorm',
            'fdb',
        ], tested.VALID_SYSTEMS)
        self.assertEqual('medications', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('medications', tested.API_UPDATE_FIELD)

    def test_item_to_codes(self):
        item = {
            'codinx': [{
                'system': '',
                'code': 'cde113',
                'display': 'The A'
            }],
            'coding': [
                {
                    'system': '',
                    'code': 'cde123',
                    'display': 'The A'
                },
                {
                    'system': '',
                    'code': 'cde124',
                    'display': 'The B'
                },
                {
                    'system': '',
                    'code': 'cde125',
                    'display': 'The C'
                },
            ],
            'codiny': [{
                'system': '',
                'code': 'cde133',
                'display': 'The A'
            }],
        }
        expected = [
            {
                'system': '',
                'code': 'cde123',
                'display': 'The A'
            },
            {
                'system': '',
                'code': 'cde124',
                'display': 'The B'
            },
            {
                'system': '',
                'code': 'cde125',
                'display': 'The C'
            },
        ]
        self.assertEqual(expected, MedicationRecordSet.item_to_codes(item))


class TestInterviewRecordSet(TestCase):

    def test_constants(self):
        tested = InterviewRecordSet([])
        self.assertIsInstance(tested, PatientEventRecordSet)
        self.assertEqual([
            'loinc',
            'snomedct',
            'rxnorm',
            'canvas',
            'internal',
        ], tested.VALID_SYSTEMS)
        self.assertEqual('noteTimestamp', tested.DATE_FIELD)
        self.assertEqual('interviews', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('interviews', tested.API_UPDATE_FIELD)

    def test_item_to_codes(self):
        # flake8: noqa
        item = {
            'results': [
                {'codeSystem': 'http://loina.org', 'code': '76504-0', 'id': 127, },
                {'codeSystem': 'http://loinc.org', 'code': '76504-1', 'id': 128, },
                {'codeSystem': 'http://loinc.org', 'code': '', 'id': 129, },
                {'codeSystem': '', 'code': '76504-3', 'id': 130},
            ],
            'questionnaires': [
                {'id': 9, 'code': '12771-1', 'codeSystem': 'http://loinx.org', },
                {'id': 3, 'code': '12771-3', 'codeSystem': 'http://loinz.org', },
            ],
            'questions': [
                {'id': 129, 'code': '76501-1', 'codeSystem': 'http://loinx.org', 'questionResponseId': 33, },
                {'id': 125, 'code': '76501-2', 'codeSystem': 'http://loiny.org', 'questionResponseId': 34, },
                {'id': 123, 'code': '76501-3', 'codeSystem': 'http://loinz.org', 'questionResponseId': 35, },
            ],
            'responses': [
                {'id': 439, 'code': '96501-1', 'codeSystem': 'http://loinx.org', 'questionResponseId': 33, },
                {'id': 435, 'code': '96501-2', 'codeSystem': 'http://loiny.org', 'questionResponseId': 34, },
                {'id': 433, 'code': '96501-3', 'codeSystem': 'http://loinz.org', 'questionResponseId': 35, },
                {'id': 437, 'code': '96501-4', 'codeSystem': 'http://loinz.org', 'questionResponseId': 35, },
            ],
        }  # yapf: disable
        expected = [
            {'code': '76504-0', 'system': 'http://loina.org', 'question_id': None, },
            {'code': '76504-1', 'system': 'http://loinc.org', 'question_id': None, },
            {'code': '12771-1', 'system': 'http://loinx.org', 'question_id': None, },
            {'code': '12771-3', 'system': 'http://loinz.org', 'question_id': None, },
            {'code': '76501-1', 'system': 'http://loinx.org', 'question_id': 33, },
            {'code': '76501-2', 'system': 'http://loiny.org', 'question_id': 34, },
            {'code': '76501-3', 'system': 'http://loinz.org', 'question_id': 35, },
            {'code': '96501-1', 'system': 'http://loinx.org', 'question_id': 33, },
            {'code': '96501-2', 'system': 'http://loiny.org', 'question_id': 34, },
            {'code': '96501-3', 'system': 'http://loinz.org', 'question_id': 35, },
            {'code': '96501-4', 'system': 'http://loinz.org', 'question_id': 35, },
        ]  # yapf: disable
        self.assertEqual(expected, InterviewRecordSet.item_to_codes(item))

    def test_find_question_response(self):

        class UnitTestQuestion(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Question for the unit tests'
            CPT = {'abc', '123'}
            SNOMEDCT = {'234', '456', '675'}

        class UnitTestResponse(ValueSet):
            OID = '1.2.3.5'
            VALUE_SET_NAME = 'Response for the unit tests'
            LOINC = {'xyz', '987'}
            SNOMEDCT = {'543', '654', '765'}

        # codes are in the question and the response
        item = [{
            'noteTimestamp': '2019-03-15 11:54:00+00:00',
            'results': [],
            'questionnaires': [],
            'questions': [
                {'id': 129, 'code': '456', 'codeSystem': 'http://snomed.info/sct', 'questionResponseId': 33, },
            ],
            'responses': [
                {'id': 439, 'code': 'xyz', 'codeSystem': 'http://loinc.org', 'questionResponseId': 33, },
            ],
        }]  # yapf: disable
        tested = InterviewRecordSet(item)
        result = tested.find_question_response(UnitTestQuestion, UnitTestResponse)
        self.assertIsInstance(result, InterviewRecordSet)
        self.assertEqual(1, len(result.records))

        # codes are in different question and response
        item = [{
            'noteTimestamp': '2019-03-15 11:54:00+00:00',
            'results': [],
            'questionnaires': [],
            'questions': [
                {'id': 129, 'code': '456', 'codeSystem': 'http://snomed.info/sct', 'questionResponseId': 33, },
            ],
            'responses': [
                {'id': 439, 'code': 'xyz', 'codeSystem': 'http://loinc.org', 'questionResponseId': 30, },
            ],
        }]  # yapf: disable
        tested = InterviewRecordSet(item)
        result = tested.find_question_response(UnitTestQuestion, UnitTestResponse)
        self.assertIsInstance(result, InterviewRecordSet)
        self.assertEqual(0, len(result.records))


class TestReferralReportRecordSet(TestCase):

    def test_constants(self):
        tested = ReferralReportRecordSet([])
        self.assertIsInstance(tested, PatientEventRecordSet)
        self.assertEqual(['snomedct', 'loinc', 'cpt'], tested.VALID_SYSTEMS)
        self.assertEqual('originalDate', tested.DATE_FIELD)
        self.assertEqual('referral_reports', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('referralReports', tested.API_UPDATE_FIELD)

    def test_item_to_codes(self):
        item = {
            'codings': [{
                'id': 5,
                'system': 'http://www.ama-assn.org/go/cpt',
                'version': '',
                'code': '37231002',
                'value': 'Present',
                'display': 'Macular Edema',
            }, {
                'id': 4,
                'system': 'http://snomed.info/sct',
                'version': '',
                'code': '430801000124103',
                'value': 'Proliferative',
                'display': 'Retinopathy',
            }, {
                'id': 6,
                'system': 'BI-RADS assessment',
                'version': '',
                'code': '24606-6',
                'value': 'benign findings',
                'display': 'BI-RADS assessment',
            }],
        }  # yapf: disable
        expected = [
            {
                'code': '37231002',
                'system': 'http://www.ama-assn.org/go/cpt',
            },
            {
                'code': '430801000124103',
                'system': 'http://snomed.info/sct',
            },
            {
                'code': '24606-6',
                'system': 'BI-RADS assessment',
            },
        ]
        result = ReferralReportRecordSet.item_to_codes(item)
        self.assertEqual(len(expected), len(result))
        for item in result:
            item_present = False
            for option in expected:
                if option['code'] == item['code'] and option['system'] == item['system']:
                    item_present = True
            self.assertTrue(item_present)


class TestImagingReportRecordSet(TestCase):

    def test_constants(self):
        tested = ImagingReportRecordSet([])
        self.assertIsInstance(tested, PatientEventRecordSet)
        self.assertEqual(['snomedct', 'loinc', 'cpt'], tested.VALID_SYSTEMS)
        self.assertEqual('originalDate', tested.DATE_FIELD)
        self.assertEqual('imaging_reports', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('imagingReports', tested.API_UPDATE_FIELD)

    def test_item_to_codes(self):
        item = {
            'codings': [{
                'id': 21,
                'system': 'http://loinc.org',
                'version': '',
                'code': '408573005',
                'value': 'Normal',
                'display': 'Status'
            }, {
                'id': 20,
                'system': 'http://www.ama-assn.org/go/cpt',
                'version': '',
                'code': '282290005',
                'value': '5',
                'display': 'Interpretation'
            }, {
                'id': 4,
                'system': 'http://snomed.info/sct',
                'version': '',
                'code': '430801000124103',
                'value': 'Proliferative',
                'display': 'Retinopathy',
            }, {
                'id': 19,
                'system': 'http://www.ama-assn.org/go/cpt',
                'version': '',
                'code': '281296001',
                'value': '11',
                'display': 'Comment'
            }],
        }  # yapf: disable
        expected = [
            {
                'code': '408573005',
                'system': 'http://loinc.org'
            },
            {
                'code': '282290005',
                'system': 'http://www.ama-assn.org/go/cpt'
            },
            {
                'code': '430801000124103',
                'system': 'http://snomed.info/sct',
            },
            {
                'code': '281296001',
                'system': 'http://www.ama-assn.org/go/cpt'
            },
        ]
        self.assertEqual(expected, ImagingReportRecordSet.item_to_codes(item))


class TestProtocolOverrideRecordSet(TestCase):

    def test_constants(self):
        tested = ProtocolOverrideRecordSet([])
        self.assertIsInstance(tested, PatientRecordSet)
        self.assertEqual(['snomedct'], tested.VALID_SYSTEMS)
        self.assertEqual('protocol_overrides', tested.PATIENT_FIELD)
        self.assertEqual('patient__key', tested.API_KEY_FIELD)
        self.assertEqual('protocolOverrides', tested.API_UPDATE_FIELD)

    def test_is_switched_off(self):
        tested = ProtocolOverrideRecordSet([{
            'protocolKey': 'TEST001v2',
            'adjustment': {
                'reference': '2018-10-01T00:00:00Z',
                'cycleDays': 19
            },
            'snooze': {
                'reference': '2018-10-01T00:00:00Z',
                'snoozedDays': 22,
                'reasonCode': '413311005',
                'reasonText': 'PATIENT_REFUSED',
                'reasonCodeSystem': 'snomedct'
            },
            'modified': '2018-10-02T21:50:09.661490Z'
        }])  # yapf: disable
        self.assertFalse(tested.all_switched_off)
        tested = ProtocolOverrideRecordSet([{
            'protocolKey': '*',
            'adjustment': {
                'reference': '2018-10-01T00:00:00Z',
                'cycleDays': 19
            },
            'snooze': {
                'reference': '2018-10-01T00:00:00Z',
                'snoozedDays': 22,
                'reasonCode': '413311005',
                'reasonText': 'PATIENT_REFUSED',
                'reasonCodeSystem': 'snomedct'
            },
            'modified': '2018-10-02T21:50:09.661490Z'
        }])  # yapf: disable
        self.assertTrue(tested.all_switched_off)

    def test_is_snoozed(self):
        tested = ProtocolOverrideRecordSet([
            {
                'protocolKey': 'TEST006v2',
                'adjustment': None,
                'snooze': {
                    'reference': '2018-09-15T00:00:00Z',
                    'snoozedDays': 12,
                    'reasonCode': '413311005',
                    'reasonText': 'PATIENT_REFUSED',
                    'reasonCodeSystem': 'snomedct'
                },
                'modified': '2018-09-15T21:50:09.661490Z'
            },
            {
                'protocolKey': 'TEST001v2',
                'adjustment': {
                    'reference': '2018-10-01T00:00:00Z',
                    'cycleDays': 19
                },
                'snooze': {
                    'reference': arrow.now(),
                    'snoozedDays': 22,
                    'reasonCode': '413311005',
                    'reasonText': 'PATIENT_REFUSED',
                    'reasonCodeSystem': 'snomedct'
                },
                'modified': '2018-10-02T21:50:09.661490Z'
            },
            {
                'protocolKey': 'TEST003v2',
                'adjustment': None,
                'snooze': {
                    'reference': '2018-09-15T00:00:00Z',
                    'snoozedDays': 12,
                    'reasonCode': '413311005',
                    'reasonText': 'PATIENT_REFUSED',
                    'reasonCodeSystem': 'snomedct'
                },
                'modified': '2018-09-15T21:50:09.661490Z'
            },
            {
                'protocolKey': 'TEST004v1',
                'adjustment': {
                    'reference': '2018-08-15T00:00:00Z',
                    'cycleDays': 60
                },
                'snooze': None,
                'modified': '2018-08-23T21:50:09.661490Z'
            }])  # yapf: disable
        # protocol is not overridden --> false
        self.assertFalse(tested.is_snoozed(['TEST005v1']))
        # snooze is not defined --> false
        self.assertFalse(tested.is_snoozed(['TEST004v1']))
        # snooze defined but past --> false
        self.assertFalse(tested.is_snoozed(['TEST003v2']))
        self.assertFalse(tested.is_snoozed([
            'TEST003v2',
            'TEST004v1',
            'TEST005v1',
        ]))
        # snooze defined and not past yet --> true
        self.assertTrue(tested.is_snoozed(['TEST001v2']))
        self.assertTrue(tested.is_snoozed([
            'TEST003v2',
            'TEST001v2',
            'TEST005v1',
        ]))

    def test_item_to_codes(self):
        item = {
            'protocolKey': 'TEST001v2',
            'adjustment': {
                'reference': '2018-10-01T00:00:00Z',
                'cycleDays': 19
            },
            'snooze': {
                'reference': arrow.now(),
                'snoozedDays': 22,
                'reasonCode': '413311005',
                'reasonText': 'PATIENT_REFUSED',
                'reasonCodeSystem': 'snomedct'
            },
            'modified': '2018-10-02T21:50:09.661490Z'
        }  # yapf: disable
        expected = [
            {
                'code': '413311005',
                'system': 'snomedct'
            },
        ]
        self.assertEqual(expected, ProtocolOverrideRecordSet.item_to_codes(item))


# --- helpers ---
class UnitTestRecordSetEvent(PatientEventRecordSet):
    VALID_SYSTEMS = ['icd10cm', 'icd10pcs', 'snomedct']
    DATE_FIELD = 'fldDate'
    PATIENT_FIELD = 'fldPatient'
    API_UPDATE_FIELD = 'updateA'


class UnitTestRecordSetPeriod(PatientPeriodRecordSet):
    VALID_SYSTEMS = ['icd10cm', 'snomedct']
    DATE_FIELD = 'fldDate'
    PATIENT_FIELD = 'fldPatient'
    API_KEY_FIELD = 'another__key'
    API_UPDATE_FIELD = 'updateB'


class UnitTestARecordSet(PatientRecordSet):
    VALID_SYSTEMS = ['icd10cm', 'snomedct']
    PATIENT_FIELD = 'fldPatient'
    API_UPDATE_FIELD = 'updateD'


class UnitTestBRecordSet(PatientRecordSet):
    VALID_SYSTEMS = ['icd10cm']
    PATIENT_FIELD = 'fldPatient'
    API_KEY_FIELD = 'another__key'
    API_UPDATE_FIELD = 'updateE'


class UnitTestNoSystemRecordSet(PatientRecordSet):
    VALID_SYSTEMS = []
    PATIENT_FIELD = 'fldPatient'
    API_UPDATE_FIELD = 'updateC'
