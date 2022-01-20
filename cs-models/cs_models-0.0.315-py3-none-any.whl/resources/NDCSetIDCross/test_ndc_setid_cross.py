from sqlalchemy.orm.exc import (
    NoResultFound,
)
from parameterized import parameterized

from test.backendtestcase import TestCase
from test.utils import second_equals_first
from src.cs_models.resources.NDCSetIDCross import NDCSetIDCross


class NDCSetIDCrossResourceTestCase(TestCase):
    def setUp(self):
        super(NDCSetIDCrossResourceTestCase, self).setUp()
        self.inst = NDCSetIDCross()

        self.ndcsetidcross1 = self.inst.create({
            "product_ndc": "12745-202",
            "package_ndc": "12745-202-02",
            "spl_set_id": "f6d677b8-fa89-4efb-984a-fd98e3e590e8",

        })

        self.ndcsetidcross2 = self.inst.create({
            "product_ndc": "52862-007",
            "package_ndc": "52862-007-12",
            "spl_set_id": "5c8f7727-5f21-4a69-8af1-c24b43571d4d",

        })

        self.valid_data = {
            "product_ndc": "0363-0871",
            "package_ndc": "0363-0871-43",
            "spl_set_id": "eea239fe-554f-4487-9312-3ab0af27d530",
        }

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
        ('product_ndc', 'ndcsetidcross1', 'product_ndc', 1),
        ('spl_set_id', 'ndcsetidcross1', 'spl_set_id', 1),
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
        ('product_ndc', '999', NoResultFound),
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
        ('product_ndc',),
        ('spl_set_id',),
    ])
    def test_one(self, field_name):
        resp = self.inst.one({
            field_name: self.ndcsetidcross1[field_name],
        })
        second_equals_first(
            self.ndcsetidcross1,
            resp,
        )
