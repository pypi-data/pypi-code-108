from copy import copy
from test.backendtestcase import TestCase
from test.utils import second_equals_first

from marshmallow import ValidationError
from parameterized import parameterized
from sqlalchemy.exc import IntegrityError

from src.cs_models.resources.Subsidiary import Subsidiary
from src.cs_models.resources.CompanySEC import CompanySEC
from src.cs_models.resources.CompanyOUS import CompanyOUS
from src.cs_models.resources.OrangeBookProduct import (
    OrangeBookProduct,
    OrangeBookProductNotFoundException,
)


class OrangeBookProductResourceTestCase(TestCase):
    def setUp(self):
        super(OrangeBookProductResourceTestCase, self).setUp()
        self.inst_subsidiary = Subsidiary()
        self.inst_sec_company = CompanySEC()
        self.inst_ous_company = CompanyOUS()
        self.inst = OrangeBookProduct()

        self.company_sec1 = self.inst_sec_company.create(
            {
                "cik_str": "200406",
                "ticker": "JNJ",
                "title": "JOHNSON & JOHNSON",
            }
        )

        self.subsidiary1 = self.inst_subsidiary.create(
            {
                "name": "Janssen Scientific Affairs, LLC",
                "company_sec_id": self.company_sec1["id"],
                "company_ous_id": None,
            }
        )

        self.ob_product1 = self.inst.create(
            {
                "appl_no": "78907",
                "appl_type": "A",
                "applicant": "SPECGX LLC",
                "applicant_full_name": "SPECGX LLC",
                "applicant_subsidiary_id": None,
                "approval_date": "Oct 30, 2009",
                "dosage_form": "TROCHE/LOZENGE",
                "ingredient": "FENTANYL CITRATE",
                "product_no": "6",
                "rld": "No",
                "rs": "No",
                "route_of_administration": "TRANSMUCOSAL",
                "strength": "EQ 1.6MG BASE",
                "te_code": "AB",
                "trade_name": "FENTANYL CITRATE",
                "type": "RX",
                "drug_set_id": None,
            }
        )
        self.valid_data = {
            "appl_no": "12312",
            "appl_type": "A",
            "applicant": "Something",
            "applicant_full_name": "some llc",
            "applicant_subsidiary_id": self.subsidiary1["id"],
            "approval_date": "Oct 30, 2009",
            "dosage_form": "TROCHE/LOZENGE",
            "ingredient": "FENTANYL CITRATE",
            "product_no": "6",
            "rld": "No",
            "rs": "No",
            "route_of_administration": "TRANSMUCOSAL",
            "strength": "EQ 1.6MG BASE",
            "te_code": "AB",
            "trade_name": "FENTANYL CITRATE",
            "type": "RX",
            "drug_set_id": None,
        }

    def test_create_validation_error_missing_fields(self):
        self.assertRaises(ValidationError, self.inst.create, {})

    def test_invalid_applicant_subsidiary_id_raises_exception(self):
        data = copy(self.valid_data)
        invalid_subsidiary_id = 3324
        self.assertRaises(
            IntegrityError,
            self.inst.create,
            {**data, **{"applicant_subsidiary_id": invalid_subsidiary_id}},
        )

    def test_create(self):
        data = copy(self.valid_data)
        response = self.inst.create(data)
        data.pop("approval_date")
        second_equals_first(data, response)

    def test_read_validation_error_blank_appl_no(self):
        self.assertRaises(
            ValidationError, self.inst.read, {"appl_no": ""},
        )

    def test_read_all(self):
        response = self.inst.read({})
        self.assertEqual(len(response), 1)

    @parameterized.expand(
        [("appl_no", 1), ("product_no", 2), ("trade_name", 2),]
    )
    def test_read_w_params(self, attr, expected_length):
        # setup
        new_ob_product = self.inst.create(
            {
                "appl_no": "123123",
                "appl_type": "A",
                "applicant": "SPECGX LLC",
                "applicant_full_name": "SPECGX LLC",
                "approval_date": "Oct 30, 2009",
                "dosage_form": "TROCHE/LOZENGE",
                "ingredient": "FENTANYL CITRATE",
                "product_no": self.ob_product1["product_no"],
                "rld": "No",
                "rs": "No",
                "route_of_administration": "TRANSMUCOSAL",
                "strength": "EQ 1.6MG BASE",
                "te_code": "AB",
                "trade_name": "FENTANYL",
                "type": "RX",
            }
        )
        self.inst.create(
            {
                "appl_no": "324234",
                "appl_type": "A",
                "applicant": "SPECGX LLC",
                "applicant_full_name": "SPECGX LLC",
                "approval_date": "Oct 30, 2009",
                "dosage_form": "TROCHE/LOZENGE",
                "ingredient": "FENTANYL CITRATE",
                "product_no": "123324234",
                "rld": "No",
                "rs": "No",
                "route_of_administration": "TRANSMUCOSAL",
                "strength": "EQ 1.6MG BASE",
                "te_code": "AB",
                "trade_name": "Copaxone",
                "type": "RX",
            }
        )

        response = self.inst.read({})
        self.assertEqual(3, len(response))

        response = self.inst.read({attr: new_ob_product[attr]})
        self.assertEqual(expected_length, len(response))

    def test_update_not_found(self):
        invalid_id = 99999
        args = []
        kwargs = {
            "id": invalid_id,
            "params": {
                "appl_no": "123123",
                "appl_type": "A",
                "applicant": "SPECGX LLC",
                "applicant_full_name": "SPECGX LLC",
                "approval_date": "Oct 30, 2009",
                "dosage_form": "TROCHE/LOZENGE",
                "ingredient": "FENTANYL CITRATE",
                "product_no": self.ob_product1["product_no"],
                "rld": "No",
                "rs": "No",
                "route_of_administration": "TRANSMUCOSAL",
                "strength": "EQ 1.6MG BASE",
                "te_code": "AB",
                "trade_name": "FENTANYL CITRATE",
                "type": "RX",
            },
        }
        self.assertRaises(
            OrangeBookProductNotFoundException,
            self.inst.update,
            *args,
            **kwargs,
        )

    @parameterized.expand(
        ["appl_no", "product_no", "drug_set_id"]
    )
    def test_update(self, field_name):
        new_data = {
            "appl_no": "2000",
            "appl_type": "ABBB",
            "applicant": "SPECGX LLC",
            "applicant_full_name": "SPECGX LLC",
            "approval_date": "Oct 30, 2009",
            "dosage_form": "TROCHE/LOZENGE",
            "ingredient": "FENTANYL CITRATE",
            "product_no": "123123123",
            "rld": "No",
            "rs": "No",
            "route_of_administration": "TRANSMUCOSAL",
            "strength": "EQ 1.6MG BASE",
            "te_code": "AB",
            "trade_name": "FENTANYL CITRATE",
            "type": "RX",
            "drug_set_id": "43a44fd3-4ba6-40c9-929f-8600f8da4222",
        }
        response = self.inst.update(
            id=self.ob_product1["id"], params=new_data,
        )
        self.assertEqual(response["id"], self.ob_product1["id"])
        self.assertEqual(
            response[field_name], new_data[field_name],
        )
        self.assertEqual(
            response["appl_type"], new_data["appl_type"],
        )
