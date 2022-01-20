import copy

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.FederalCaseRef import (
    FederalCaseRef,
)
from src.cs_models.resources.FederalCaseRef.models import (
    FederalCaseRefModel,
)
from src.cs_models.resources.File import File
from src.cs_models.database import db_session


class FederalCaseRefResourceTestCase(TestCase):
    def setUp(self):
        super(FederalCaseRefResourceTestCase, self).setUp()

        self.inst_file = File()

        self.inst = FederalCaseRef()

        self.file1 = self.inst_file.create(
            {
                "file_format": "html",
                "s3_bucket_name": "federal-case-pages",
                "s3_key_name": "something.html",
            }
        )

        self.federal_case_ref1 = self.inst.create({
            'case_name': '140 S.Ct. 11',
            'volume': 140,
            'reporter_type': 'S.Ct.',
            'page': 10,
            'title': 'PEARSON v. U.S., Supreme Court of United States.',
            'link': 'https://www.leagle.com/decision/insco20190715c80',
        })

        self.valid_data = {
            'case_name': '947 F.3d 139',
            'volume': 947,
            'reporter_type': 'F.3d',
            'page': 139,
            'title': 'U.S. v. TYSON, United States Court of Appeals, Third Circuit.',
            'link': 'https://www.leagle.com/decision/infco20200115128',
        }

    @parameterized.expand([
        ('case_name',),
        ('volume',),
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
        second_equals_first(
            self.valid_data,
            resp,
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

    def test_delete(self):
        self.inst.delete(id=self.federal_case_ref1['id'])

        q = self._build_query(federal_case_ref_id=self.federal_case_ref1['id'])

        assert q.first() is None

    def test_upsert_creates_new_row(self):
        q = db_session.query(FederalCaseRefModel)
        assert len(q.all()) == 1
        self.inst.upsert(self.valid_data)
        q = db_session.query(FederalCaseRefModel)
        assert len(q.all()) == 2

    def test_upsert_updates_existing_row(self):
        data = {
            'case_name': self.federal_case_ref1['case_name'],
            'volume': self.federal_case_ref1['volume'],
            'reporter_type': self.federal_case_ref1['reporter_type'],
            'page': self.federal_case_ref1['page'],
            'title': self.federal_case_ref1['title'],
            'link': self.federal_case_ref1['link'],
        }
        q = db_session.query(FederalCaseRefModel)
        assert len(q.all()) == 1
        response = self.inst.upsert(data)
        q = db_session.query(FederalCaseRefModel)
        assert len(q.all()) == 1
        second_equals_first(data, response)

    @parameterized.expand([
        ('volume',),
        ('page',),
    ])
    def test_upsert_raises_validation_error(self, field_to_pop):
        base_data = copy.copy(self.valid_data)
        base_data.pop(field_to_pop)
        self.assertRaises(
            ValidationError,
            self.inst.upsert,
            base_data,
        )

    @staticmethod
    def _build_query(federal_case_ref_id: int) -> Query:
        q = db_session.query(
            FederalCaseRefModel,
        ).filter_by(id=federal_case_ref_id)
        return q
