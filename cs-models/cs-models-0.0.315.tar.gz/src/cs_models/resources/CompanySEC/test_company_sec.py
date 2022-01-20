import copy

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.CompanySEC import (
    CompanySEC,
)
from src.cs_models.resources.CompanySEC.models import (
    CompanySECModel,
)
from src.cs_models.database import db_session


class CompanySECResourceTestCase(TestCase):
    def setUp(self):
        super(CompanySECResourceTestCase, self).setUp()
        self.inst = CompanySEC()

        self.company_sec1 = self.inst.create({
            'cik_str': '1652044',
            'ticker': 'GOOG',
            'title': 'Alphabet Inc.',
        })

        self.valid_data = {
            'cik_str': '1577552',
            'ticker': 'BABA',
            'title': 'Alibaba Group Holding Ltd',
        }

    @parameterized.expand([
        ('cik_str',),
        ('title',),
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
                'cik_str': self.company_sec1['cik_str'],
                'ticker': self.company_sec1['ticker'],
                'title': self.company_sec1['title'],
            },
        )

    def test_create(self):
        resp = self.inst.create(self.valid_data)
        second_equals_first(
            self.valid_data,
            resp,
        )

    def test_delete(self):
        self.inst.delete(id=self.company_sec1['id'])

        q = self._build_query(company_sec_id=self.company_sec1['id'])

        assert q.first() is None

    def test_upsert_creates_new_row(self):
        q = db_session.query(CompanySECModel)
        assert len(q.all()) == 1
        self.inst.upsert(self.valid_data)
        q = db_session.query(CompanySECModel)
        assert len(q.all()) == 2

    def test_upsert_updates_existing_row(self):
        data = {
            'cik_str': self.company_sec1['cik_str'],
            'ticker': self.company_sec1['ticker'],
            'title': 'Google Inc.',
        }
        q = db_session.query(CompanySECModel)
        assert len(q.all()) == 1
        response = self.inst.upsert(data)
        q = db_session.query(CompanySECModel)
        assert len(q.all()) == 1
        second_equals_first(data, response)

    @parameterized.expand([
        ('cik_str',),
        ('title',),
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
    def _build_query(company_sec_id: int) -> Query:
        q = db_session.query(
            CompanySECModel,
        ).filter_by(id=company_sec_id)
        return q
