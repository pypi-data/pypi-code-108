import copy
from marshmallow import ValidationError
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.UserSearchHistoryItem import (
    UserSearchHistoryItem,
)


class UserSearchHistoryItemResourceTestCase(TestCase):
    def setUp(self):
        super(UserSearchHistoryItemResourceTestCase, self).setUp()
        self.inst = UserSearchHistoryItem()

        self.user_id1 = '1000'
        self.user_id2 = '2000'

        self.search_item1 = self.inst.create({
            'user_id': self.user_id1,
            'search_term': 'copaxone',
            'search_type': 'drug',
        })

        self.search_item2 = self.inst.create({
            'user_id': self.user_id1,
            'search_term': 'latuda',
            'search_type': 'drug',
        })

        self.search_item3 = self.inst.create({
            'user_id': self.user_id2,
            'search_term': 'latuda',
            'search_type': 'drug',
        })

        self.search_item4 = self.inst.create({
            'user_id': self.user_id2,
            'search_term': 'teva',
            'search_type': 'company',
        })

        self.valid_data = {
            'user_id': self.user_id1,
            'search_term': 'IPR2015-001',
            'search_type': 'proceeding',
        }

    @parameterized.expand([
        ('user_id',),
        ('search_term',),
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
        second_equals_first(self.valid_data, resp)

    def test_read(self):
        resp = self.inst.read({})
        self.assertEqual(4, len(resp))

    @parameterized.expand([
        ('id', 'search_item1', 'id', 1),
        ('user_id', 'search_item1', 'user_id', 2),
        ('search_term', 'search_item2', 'search_term', 2),
        ('search_type', 'search_item2', 'search_type', 3),
    ])
    def test_read_w_params(
        self,
        field_name,
        attr,
        attr_field,
        expected_length,
    ):
        resp = self.inst.read({})
        self.assertEqual(4, len(resp))

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
