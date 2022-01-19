import copy
from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.DrugIndication import DrugIndication


class DrugIndicationResourceTestCase(TestCase):
    def setUp(self):
        super(DrugIndicationResourceTestCase, self).setUp()
        self.inst = DrugIndication()

        self.indication1 = self.inst.create({
            'set_id': '3b36645c-de5e-4263-ae06-2f6ff6a9add2',
            'lowercase_indication': 'plaque psoriasis',
            'indication': "plaque psoriasis",

        })

        self.indication2 = self.inst.create({
            'set_id': 'b5cdf4fd-9c95-441a-83eb-fbdb71ee42fa',
            'lowercase_indication': 'asthma',
            'indication': "asthma",
        })

        self.valid_data = {
            'set_id': '543dda2c-7fce-4cd3-9d0a-0a167c71f223',
            'lowercase_indication': "ulcerative colitis",
            'indication': "ulcerative colitis",
        }

    @parameterized.expand([
        ('set_id',),
    ])
    def test_create_validation_error_missing_field(self, field_to_pop):
        base_data = copy.copy(self.valid_data)
        base_data.pop(field_to_pop)
        self.assertRaises(
            ValidationError,
            self.inst.create,
            base_data,
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        expected_data = {
            **self.valid_data,
        }
        second_equals_first(expected_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

    @parameterized.expand([
        ('id', 'indication1', 'id', 1),
        ('indication', 'indication1', 'indication', 2),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

        resp = self.inst.read({
            field_name: getattr(self, attr)[attr_field],
        })
        self.assertEqual(expected_length, len(resp))

    @parameterized.expand([
        ('id', 999, NoResultFound),
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
        ('id',),
        ('set_id',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.indication1[field_name],
        })
        second_equals_first(
            self.indication1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'set_id': self.valid_data['set_id'],
            }
        )

    def test_upsert_creates_new_entry(self):
        data = copy.copy(self.valid_data)
        self.assertEqual(2, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            **self.valid_data,
            **{'set_id': self.indication1['set_id'],
               'lowercase_indication': self.indication1[
                   'lowercase_indication'],
               'indication': self.indication1['indication']
               },
        }
        resp = self.inst.upsert(data)
        expected_data = {
            **data,
        }
        second_equals_first(
            expected_data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))
