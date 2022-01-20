import copy

from test.backendtestcase import TestCase
from test.utils import second_equals_first

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from parameterized import parameterized

from src.cs_models.resources.PTAB2Document import PTAB2Document
from src.cs_models.resources.DocumentReference import DocumentReference
from src.cs_models.resources.File import File


class DocumentReferenceResourceTestCase(TestCase):
    def setUp(self):
        super(DocumentReferenceResourceTestCase, self).setUp()

        self.inst_file = File()
        self.inst_ptab2_document = PTAB2Document()
        self.inst = DocumentReference()

        self.ptab2_document1 = self.inst_ptab2_document.create(
            {
                "document_category": "Exhibits",
                "document_filing_date": "05-08-2019",
                "document_identifier": "1000",
                "document_name": "Exhibit 1066 - EC-Naprosyn 2004 label.pdf",
                "document_number": "1066",
                "document_size": "-",
                "document_title_text": "EC Naprosyn 2004 label",
                "document_type_name": "EXHIBIT",
                "filing_party_category": "-",
                "media_type_category": "-",
                "petitioner_application_number_text": "-",
                "petitioner_counsel_name": "Alan H. Pollack",
                "petitioner_grant_date": "-",
                "petitioner_group_art_unit_number": "-",
                "petitioner_inventor_name": "-",
                "petitioner_party_name": "Mylan Pharmaceuticals Inc.",
                "petitioner_patent_number": "-",
                "petitioner_patent_owner_name": "-",
                "petitioner_technology_center_number": "-",
                "proceeding_number": "IPR2018-00272",
                "proceeding_type_category": "AIA Trial",
                "respondent_application_number_text": "14980639",
                "respondent_counsel_name": "Thomas Blinka",
                "respondent_grant_date": "07-19-2016",
                "respondent_group_art_unit_number": "1617",
                "respondent_inventor_name": "-",
                "respondent_party_name": "Horizon Pharma USA, Inc.",
                "respondent_patent_number": "9393208",
                "respondent_patent_owner_name": "AULT et al",
                "respondent_technology_center_number": "1600",
                "subproceeding_type_category": "IPR",
            }
        )

        self.file1 = self.inst_file.create(
            {
                "file_format": "html",
                "s3_bucket_name": "federal-case-pages",
                "s3_key_name": "something.html",
            }
        )

        self.document_reference1 = self.inst.create(
            {
                "ptab2_document_id": self.ptab2_document1["id"],
                "type": "FEDERAL_CASE",
                "value": "1:16-cv-00469 (filed Feb. 26, 2016)",
                "federal_case_number": "123",
                "link": "www.abc.com",
                "pages": "[23, 78, 81]",
            }
        )

        self.document_reference2 = self.inst.create(
            {
                "ptab2_document_id": self.ptab2_document1["id"],
                "type": "CIVIL_CASE",
                "value": "Something else",
                "pages": "[12, 42, 55]",
            }
        )

        self.valid_data = {
            "ptab2_document_id": self.ptab2_document1["id"],
            "type": "FEDERAL_CASE",
            "value": "778 F.3d 1271, 1279",
            "pages": "[34, 35, 67, 73]",
        }

    @parameterized.expand(
        [("ptab2_document_id",), ("type",), ("value",),]
    )
    def test_create_validation_error_missing_field(self, field_to_pop):
        data = copy.copy(self.valid_data)
        data.pop(field_to_pop)
        self.assertRaises(
            ValidationError, self.inst.create, data,
        )

    def test_create_raises_exception_if_null_ptab2_document_id(self):
        invalid_ptab2_document_id = None
        data = {
            **self.valid_data,
            **{"ptab2_document_id": invalid_ptab2_document_id},
        }
        self.assertRaises(
            ValidationError, self.inst.create, data,
        )

    def test_create_violates_fk_constraint(self):
        invalid_ptab2_document_id = 12323423
        data = {
            **self.valid_data,
            **{"ptab2_document_id": invalid_ptab2_document_id},
        }
        self.assertRaises(
            IntegrityError, self.inst.create, data,
        )

    def test_create_violates_fk_constraint_file_id(self):
        invalid_federal_case_file_id = 12323423
        data = {
            **self.valid_data,
            **{"federal_case_file_id": invalid_federal_case_file_id},
        }
        self.assertRaises(
            IntegrityError, self.inst.create, data,
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(2, len(resp))

    @parameterized.expand(
        [
            ("ptab2_document_id", "ptab2_document1", "id", 2),
            ("type", "document_reference1", "type", 1),
            ("value", "document_reference1", "value", 1),
            (
                "federal_case_number",
                "document_reference1",
                "federal_case_number",
                1,
            ),
            (
                "link",
                "document_reference1",
                "link",
                1,
            ),
        ]
    )
    def test_read_w_params(
        self, field_name, attr, attr_field, expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(len(resp), 2)

        resp = self.inst.read({field_name: getattr(self, attr)[attr_field],})
        self.assertEqual(expected_length, len(resp))

    @parameterized.expand(
        [("id", 999, NoResultFound),]
    )
    def test_one_raises_exception(self, field_name, field_value, exception):
        self.assertRaises(
            exception, self.inst.one, {field_name: field_value,},
        )

    @parameterized.expand(
        [("id",), ("type",), ("value",),]
    )
    def test_one(self, field_name):
        resp = self.inst.one(
            {field_name: self.document_reference1[field_name],}
        )
        second_equals_first(
            self.document_reference1, resp,
        )

    def test_update(self):
        new_data = {
            "value": "something new",
            "type": "ny",
            "federal_case_headline": "some headline",
            "federal_case_number": "case number 123",
            "link": "www.asd.com",
            "federal_case_file_id": self.file1["id"],
            "pages": "[23, 45, 46]",
        }
        resp = self.inst.update(
            id=self.document_reference1["id"], params=new_data,
        )
        expected_result = {
            **self.document_reference1,
            **new_data,
            # the following fields cannot be updated
            **{
                "value": self.document_reference1["value"],
                "type": self.document_reference1["type"],
            },
        }

        second_equals_first(
            expected_result, resp, fields_to_ignore=["updated_at"],
        )

    def test_create_without_pages_raises_exception(self):
        data = {
            **self.valid_data,
            **{"pages": None},
        }
        self.assertRaises(
            ValidationError, self.inst.create, data,
        )

    def test_update_without_pages_raises_exception(self):
        new_data = {
            "value": "something new",
            "type": "ny",
            "federal_case_headline": "some headline",
            "federal_case_number": "case number 123",
            "link": "www.asd.com",
            "federal_case_file_id": self.file1["id"],
            "pages": None,
        }
        self.assertRaises(
            ValidationError,
            self.inst.update,
            id=self.document_reference1["id"],
            params=new_data,
        )

    def test_delete_not_found(self):
        invalid_id = 99999
        self.assertRaises(
            NoResultFound, self.inst.delete, invalid_id,
        )

    def test_delete(self):
        response = self.inst.one({"id": self.document_reference1["id"],})
        self.inst.delete(id=response["id"])
        self.assertRaises(
            NoResultFound,
            self.inst.one,
            {"id": self.document_reference1["id"]},
        )

    def test_bulk_delete(self):
        response = self.inst.read({})
        self.assertEqual(2, len(response))

        self.inst.bulk_delete(ptab2_document_id=self.ptab2_document1["id"])

        response = self.inst.read({})
        self.assertEqual(0, len(response))
