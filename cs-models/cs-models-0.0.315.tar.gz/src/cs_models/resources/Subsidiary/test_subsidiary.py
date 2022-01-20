import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.Subsidiary import Subsidiary
from src.cs_models.resources.CompanySEC import CompanySEC
from src.cs_models.resources.CompanyOUS import CompanyOUS


class SubsidiaryResourceTestCase(TestCase):
    def setUp(self):
        super(SubsidiaryResourceTestCase, self).setUp()
        self.inst = Subsidiary()
        self.inst_sec_company = CompanySEC()
        self.inst_ous_company = CompanyOUS()

        self.company_sec1 = self.inst_sec_company.create({
            'cik_str': '200406',
            'ticker': 'JNJ',
            "title": "JOHNSON & JOHNSON",
        })

        self.company_sec2 = self.inst_sec_company.create({
            "cik_str": "816284",
            "ticker": "CELG",
            "title": "CELGENE CORP /DE/"
        })

        self.company_ous1 = self.inst_ous_company.create({
            'name': 'Aurobindo Pharma',
            'ticker': 'AUROPHARMA',
            'exchange': 'NSE',
        })

        self.subsidiary1 = self.inst.create({
            'name': 'Janssen Scientific Affairs, LLC',
            'company_sec_id': self.company_sec1['id'],
            'company_ous_id': None,
        })

        self.subsidiary2 = self.inst.create({
            'name': 'Celgene International II SARL',
            'company_sec_id': self.company_sec2['id'],
            'company_ous_id': None,
        })

        self.subsidiary3 = self.inst.create({
            'name': 'Aurobindo Pharma Pvt. Ltd.',
            'company_sec_id': None,
            'company_ous_id': self.company_ous1['id'],
        })

        self.valid_data = {
            'name': 'Janssen Research & Development, LLC',
            'company_sec_id': self.company_sec1['id'],
            'company_ous_id': None,
        }

    @parameterized.expand([
        ('name',),
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
            {'name': self.subsidiary1['name']},
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(3, len(resp))

    @parameterized.expand([
        ('id', 'subsidiary1', 'id', 1),
        ('name', 'subsidiary1', 'name', 1),
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
        ('name',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.subsidiary1[field_name],
        })
        second_equals_first(
            self.subsidiary1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'company_sec_id': self.valid_data['company_sec_id'],
            }
        )

    def test_upsert_both_company_sec_company_ous_validation_error(self):
        data = {
            **self.valid_data,
            **{
               'company_ous_id': self.company_ous1['id'],
               },
        }
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            data
        )

    def test_upsert_creates_new_entry(self):
        data = copy.copy(self.valid_data)
        self.assertEqual(3, len(self.inst.read({})))
        self.inst.upsert(data)
        self.assertEqual(4, len(self.inst.read({})))

    def test_upsert_updates_existing_row(self):
        data = {
            **self.valid_data,
            **{'name': self.subsidiary1['name'],
               'company_sec_id': self.company_sec1['id'],
               },
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(3, len(self.inst.read({})))

    def test_upsert_with_invalid_company_sec_id(self):
        invalid_id = 9999999
        data = {
            **self.valid_data,
            **{'name': self.subsidiary1['name'],
               'company_sec_id': invalid_id,
               },
        }
        self.assertRaises(
            IntegrityError,
            self.inst.upsert,
            data,
        )
