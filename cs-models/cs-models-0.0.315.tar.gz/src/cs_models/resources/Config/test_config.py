import copy
from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.Config import Config


class ConfigResourceTestCase(TestCase):
    def setUp(self):
        super(ConfigResourceTestCase, self).setUp()
        self.inst = Config()

        self.config1 = self.inst.create({
            'table_name': 'ptab2_documents',
            'field_name': 'document_filing_date',
            'latest_date': '06-08-2020',
        })

        self.valid_data = {
            'table_name': 'ptab2_proceedings',
            'field_name': 'accorded_filing_date',
            'latest_date': '01-01-2020',
        }

    @parameterized.expand([
        ('latest_date',),
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
            **{
                'latest_date': '2020-01-01T00:00:00+00:00',
            }
        }
        second_equals_first(expected_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(1, len(resp))

    @parameterized.expand([
        ('id', 'config1', 'id', 1),
        ('table_name', 'config1', 'table_name', 1),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(1, len(resp))

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
        ('field_name',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.config1[field_name],
        })
        second_equals_first(
            self.config1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'latest_date': self.valid_data['latest_date'],
            }
        )

    def test_upsert_creates_new_entry(self):
        data = copy.copy(self.valid_data)
        self.assertEqual(1, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(2, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            **self.valid_data,
            **{'table_name': self.config1['table_name'],
               'field_name': self.config1['field_name'],
               },
        }
        resp = self.inst.upsert(data)
        expected_data = {
            **data,
            **{
                'latest_date': '2020-01-01T00:00:00+00:00',
            }
        }
        second_equals_first(
            expected_data,
            resp,
        )
        self.assertEqual(1, len(self.inst.read({})))
