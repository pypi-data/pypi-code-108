import copy
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.SubsidiarySponsorMapping import (
    SubsidiarySponsorMapping,
)
from src.cs_models.resources.Subsidiary import Subsidiary
from src.cs_models.resources.CompanySEC import CompanySEC
from src.cs_models.resources.CompanyOUS import CompanyOUS


class SubsidiarySponsorResourceTestCase(TestCase):
    def setUp(self):
        super(SubsidiarySponsorResourceTestCase, self).setUp()
        self.inst = SubsidiarySponsorMapping()
        self.inst_sec_company = CompanySEC()
        self.inst_ous_company = CompanyOUS()
        self.inst_subsidiary = Subsidiary()

        self.company_sec1 = self.inst_sec_company.create({
            'cik_str': '1048477',
            'ticker': 'BMRN',
            "title": "BIOMARIN PHARMACEUTICAL INC",
        })

        self.company_sec2 = self.inst_sec_company.create({
            "cik_str": "816284",
            "ticker": "QURE",
            "title": "uniQure"
        })

        self.company_ous1 = self.inst_ous_company.create({
            'name': 'Aurobindo Pharma',
            'ticker': 'AUROPHARMA',
            'exchange': 'NSE',
        })

        self.subsidiary1 = self.inst_subsidiary.create({
            'name': 'BioMarin Pharmaceutical',
            'company_sec_id': self.company_sec1['id'],
            'company_ous_id': None,
        })

        self.subsidiary2 = self.inst_subsidiary.create({
            'name': 'uniQure Biopharma B.V.',
            'company_sec_id': self.company_sec2['id'],
            'company_ous_id': None,
        })

        self.subsidiary_sponsor_mapping1 = self.inst.create({
            'sponsor_id': 8810281,
            'sponsor_name': 'UniQure Biopharma B.V.',
            'subsidiary_id': self.subsidiary2['id'],
        })

        self.subsidiary_sponsor_mapping2 = self.inst.create({
            'sponsor_id': 8761999,
            'sponsor_name': 'BioMarin Pharmaceutical',
            'subsidiary_id': self.subsidiary1['id'],
        })

        self.valid_data = {
            'sponsor_id': 8825223,
            'sponsor_name': 'Celgene International Sarl',
            'subsidiary_id': self.subsidiary1['id'],
        }

    @parameterized.expand([
        ('sponsor_id',),
        ('sponsor_name',),
        ('subsidiary_id',),
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
                'sponsor_id': self.subsidiary_sponsor_mapping1['sponsor_id'],
                'sponsor_name': self.subsidiary_sponsor_mapping1['sponsor_name'],
                'subsidiary_id': self.subsidiary_sponsor_mapping1['subsidiary_id'],
             },
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

    @parameterized.expand([
        ('sponsor_id', 'subsidiary_sponsor_mapping1', 'sponsor_id', 1),
        ('subsidiary_id', 'subsidiary_sponsor_mapping1', 'subsidiary_id', 1),
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
        ('sponsor_id',),
        ('subsidiary_id',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.subsidiary_sponsor_mapping1[field_name],
        })
        second_equals_first(
            self.subsidiary_sponsor_mapping1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'sponsor_id': self.valid_data['sponsor_id'],
                'subsidiary_id': None,
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
            **{'sponsor_id': self.subsidiary_sponsor_mapping1['sponsor_id'],
               'subsidiary_id': self.subsidiary2['id'],
               },
        }
        resp = self.inst.upsert(data)
        second_equals_first(
            data,
            resp,
        )
        self.assertEqual(2, len(self.inst.read({})))

    def test_upsert_with_invalid_subsidiary_id(self):
        invalid_id = None
        data = {
            **self.valid_data,
            **{'sponsor_id': self.subsidiary_sponsor_mapping1['sponsor_id'],
               'subsidiary_id': invalid_id,
               },
        }
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            data,
        )
