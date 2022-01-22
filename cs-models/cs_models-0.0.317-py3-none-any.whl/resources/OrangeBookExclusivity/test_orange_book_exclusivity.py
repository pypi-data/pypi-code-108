import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.OrangeBookExclusivity import (
    OrangeBookExclusivity,
)
from src.cs_models.utils.utils import convert_string_to_datetime


class OrangeBookExclusivityResourceTestCase(TestCase):
    def setUp(self):
        super(OrangeBookExclusivityResourceTestCase, self).setUp()
        self.inst = OrangeBookExclusivity()

        self.ob_exclusivity1 = self.inst.create({
            'appl_no': '1000',
            'appl_type': 'A',
            'product_no': '1',
            'exclusivity_code': 'ODE-64',
            'exclusivity_date': 'Apr 4, 2021',
        })

        self.ob_exclusivity2 = self.inst.create({
            'appl_no': '1000',
            'appl_type': 'A',
            'product_no': '2',
            'exclusivity_code': 'ODE-64',
            'exclusivity_date': 'Apr 4, 2021',
        })

        self.ob_exclusivity3 = self.inst.create({
            'appl_no': '2000',
            'appl_type': 'A',
            'product_no': '1',
            'exclusivity_code': 'ODE-64',
            'exclusivity_date': 'Apr 4, 2021',
        })

        self.valid_data = {
            'appl_no': '2000',
            'appl_type': 'A',
            'product_no': '2',
            'exclusivity_code': 'ODE-64',
            'exclusivity_date': 'Apr 5, 2021',
        }

    @parameterized.expand([
        ('appl_type',),
        ('appl_no',),
        ('product_no',),
        ('exclusivity_code',),
    ])
    def test_create_validation_error_missing_field(self, field_to_pop):
        base_data = copy.copy(self.valid_data)
        base_data.pop(field_to_pop)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            base_data,
        )

    def test_create_violates_unique_constraint(self):
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            {
                **self.valid_data,
                **{'product_no': self.ob_exclusivity3['product_no']},
            },
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        expected_data = {
            **self.valid_data,
            **{'exclusivity_date': (
                f"{self.valid_data['exclusivity_date']}+00:00")},
        }
        second_equals_first(
            expected_data,
            resp,
        )

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('id', 'ob_exclusivity1', 'id', 1),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

        resp = self.inst.read({
            field_name: getattr(self, attr)[attr_field],
        })
        self.assertEqual(expected_length, len(resp))

    @parameterized.expand([
        ('id', 999, NoResultFound),
        ('appl_no', '1000', MultipleResultsFound),
    ])
    def test_one_raises_exception(self, field_name, field_value, exception):
        self.assertRaises(
            exception,
            self.inst.one,
            {
                field_name: field_value,
            },
        )

    @parameterized.expand([
        (['id'],),
        (['appl_type', 'appl_no', 'product_no', 'exclusivity_code'],)
    ])
    def test_one(self, query_fields):
        query_params = {}
        for field in query_fields:
            query_params[field] = self.ob_exclusivity1[field]

        resp = self.inst.one(query_params)
        second_equals_first(
            self.ob_exclusivity1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'appl_no': self.valid_data['appl_no'],
            }
        )

    def test_upsert_creates_new_entry(self):
        data = copy.copy(self.valid_data)
        self.assertEqual(3, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(4, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            **self.valid_data,
            **{
                'appl_type': self.ob_exclusivity1['appl_type'],
                'appl_no': self.ob_exclusivity1['appl_no'],
                'product_no': self.ob_exclusivity1['product_no'],
                'exclusivity_code': self.ob_exclusivity1['exclusivity_code'],
            },
        }
        self.assertEqual(3, len(self.inst.read({})))
        resp = self.inst.upsert(data)

        second_equals_first(
            {
                **data,
                **{'exclusivity_date': (
                    f"{data['exclusivity_date']}+00:00")}
            },
            resp,
        )
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_updates_exclusivity_date(self):
        # greater than what's already there
        raw_exclusivity_date = 'Apr 10, 2021'
        data = {
            **self.valid_data,
            **{
                'appl_type': self.ob_exclusivity1['appl_type'],
                'appl_no': self.ob_exclusivity1['appl_no'],
                'product_no': self.ob_exclusivity1['product_no'],
                'exclusivity_code': self.ob_exclusivity1['exclusivity_code'],
                'exclusivity_date': raw_exclusivity_date,
            },
        }
        self.assertEqual(3, len(self.inst.read({})))
        resp = self.inst.upsert(data)

        exclusivity_date = convert_string_to_datetime(
            date=raw_exclusivity_date,
            string_format='%b %d, %Y',
        )
        expected_exclusivity_date = f"{exclusivity_date}+00:00"

        second_equals_first(
            {
                **data,
                **{'exclusivity_date': expected_exclusivity_date},
            },
            resp,
        )
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_does_not_update_exclusivity_date(self):
        # less than what's already there
        raw_exclusivity_date = 'Apr 1, 2021'
        data = {
            **self.valid_data,
            **{
                'appl_type': self.ob_exclusivity1['appl_type'],
                'appl_no': self.ob_exclusivity1['appl_no'],
                'product_no': self.ob_exclusivity1['product_no'],
                'exclusivity_code': self.ob_exclusivity1['exclusivity_code'],
                'exclusivity_date': raw_exclusivity_date,
            },
        }
        self.assertEqual(3, len(self.inst.read({})))
        resp = self.inst.upsert(data)

        expected_exclusivity_date = self.ob_exclusivity1['exclusivity_date']
        second_equals_first(
            {
                **data,
                **{'exclusivity_date': expected_exclusivity_date},
            },
            resp,
        )
        self.assertEqual(3, len(self.inst.read({})))
