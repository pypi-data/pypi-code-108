import copy
from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.Subsidiary import Subsidiary
from src.cs_models.resources.CompanySEC import CompanySEC
from src.cs_models.resources.CompanyOUS import CompanyOUS
from src.cs_models.resources.NDC import NDC


class NDCResourceTestCase(TestCase):
    def setUp(self):
        super(NDCResourceTestCase, self).setUp()
        self.inst_subsidiary = Subsidiary()
        self.inst_sec_company = CompanySEC()
        self.inst_ous_company = CompanyOUS()
        self.inst = NDC()

        self.company_sec1 = self.inst_sec_company.create(
            {
                "cik_str": "200406",
                "ticker": "TEVA",
                "title": "Teva Pharmaceuticals",
            }
        )

        self.company_sec2 = self.inst_sec_company.create(
            {
                "cik_str": "332434",
                "ticker": "RHBBY",
                "title": "ROCHE",
            }
        )

        self.subsidiary1 = self.inst_subsidiary.create(
            {
                "name": "Teva Pharma USA",
                "company_sec_id": self.company_sec1["id"],
                "company_ous_id": None,
            }
        )

        self.subsidiary2 = self.inst_subsidiary.create(
            {
                "name": "Roche",
                "company_sec_id": self.company_sec2["id"],
                "company_ous_id": None,
            }
        )

        self.ndc1 = self.inst.create({
            "spl_id": "10a84bba-6ac6-4a54-9c2b-55d39a232d59",
            'appl_no': "761083",
            'appl_type': 'B',
            'spl_set_id': None,
            "product_ndc": "50242-920",
            "package_ndc": "50242-920-01",
            "route": "Subcutaneous",
            "dosage_form": "Injection, Solution",
            "generic_name": "emicizumab",
            "labeler_name": "Genentech, Inc.",
            "brand_name": "Hemlibra",
            "marketing_category": "BLA",
            "labeler_subsidiary_id": self.subsidiary2["id"],
        })

        self.ndc2 = self.inst.create({
            "spl_id": "15ecddea-ee95-45d1-a5cc-ba1e530b3847",
            "appl_no": "020622",
            'appl_type': 'N',
            'spl_set_id': None,
            "product_ndc": "68546-317",
            "package_ndc": "68546-317-01",
            "route": "Oral",
            "dosage_form": "Tablet",
            "generic_name": "Glatiramer Acetate",
            "labeler_name": "Teva Neuroscience, Inc.",
            "brand_name_base": "Copaxone",
            "marketing_category": "NDA",
            "labeler_subsidiary_id": self.subsidiary1["id"],
        })

        self.valid_data = {
            "spl_id": "9f6112fb-78ef-43cf-8ae3-36370eb45468",
            "appl_no": "021658",
            'appl_type': 'N',
            'spl_set_id': "9f6112fb-78ef-43cf-8ae3-36370eb45468",
            "product_ndc": "70515-711",
            "package_ndc": "70515-711-01",
            "route": "Oral",
            "dosage_form": "Tablet",
            "generic_name": "ciclesonide",
            "labeler_name": "Covis Pharma",
            "brand_name": "Alvesco",
            "marketing_category": "NDA",
            "labeler_subsidiary_id": self.subsidiary1["id"],
        }

    @parameterized.expand([
        ('spl_id',),
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
        ('id', 'ndc1', 'id', 1),
        ('spl_id', 'ndc1', 'spl_id', 1),
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
        ('spl_id',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.ndc1[field_name],
        })
        second_equals_first(
            self.ndc1,
            resp,
        )

    def test_upsert_validation_error(self):
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            {
                'spl_id': self.valid_data['spl_id'],
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
            **{'spl_id': self.ndc1['spl_id'],
               'appl_no': self.ndc1['appl_no'],
               'spl_set_id': self.ndc1['spl_set_id'],
               'product_ndc': self.ndc1['product_ndc'],
               'generic_name': self.ndc1['generic_name'],
               "route": self.ndc1["route"],
               "dosage_form": self.ndc1["dosage_form"],
               'labeler_name': self.ndc1['labeler_name'],
               'brand_name': self.ndc1['brand_name'],
               'marketing_category': self.ndc1['marketing_category'],
               "labeler_subsidiary_id": self.subsidiary2["id"],
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
