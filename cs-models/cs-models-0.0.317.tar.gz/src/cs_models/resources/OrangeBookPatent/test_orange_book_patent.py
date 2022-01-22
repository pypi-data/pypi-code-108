from marshmallow import ValidationError
from parameterized import parameterized

from test.backendtestcase import TestCase
from src.cs_models.resources.OrangeBookPatent import (
    OrangeBookPatent,
    OrangeBookPatentNotFoundException,
)


class OrangeBookPatentResourceTestCase(TestCase):
    def setUp(self):
        super(OrangeBookPatentResourceTestCase, self).setUp()
        self.inst = OrangeBookPatent()
        self.ob_patent1 = self.inst.create({
            'appl_no': '22101',
            'appl_type': 'N',
            'delist_flag': '',
            'drug_product_flag': '',
            'drug_substance_flag': '',
            'patent_expire_date': 'Oct 30, 2009',
            'patent_no': '6428810*PED',
            'patent_use_code': 'U-735',
            'product_no': '1',
            'submission_date': ''
        })

    def test_create_validation_error_missing_fields(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {},
        )

    def test_create_validation_error_blank_product_no(self):
        self.assertRaises(
            ValidationError,
            self.inst.create,
            {
                'appl_no': '123',
                'appl_type': 'N',
                'delist_flag': '',
                'drug_product_flag': '',
                'drug_substance_flag': '',
                'patent_expire_date': 'Oct 30, 2009',
                'patent_no': '6428810',
                'patent_use_code': 'U-905',
                'product_no': '',
                'submission_date': ''
            },
        )

    def test_create(self):
        data = {
            'appl_no': '2000',
            'appl_type': 'N',
            'delist_flag': '',
            'drug_product_flag': '',
            'drug_substance_flag': '',
            'patent_expire_date': 'Oct 30, 2009',
            'patent_no': '6428810*PED',
            'patent_use_code': 'No Use Code',
            'product_no': '12',
            'submission_date': ''
        }
        response = self.inst.create(data)
        self.assertEqual(data['product_no'], response['product_no'])
        self.assertEqual(data['patent_no'], response['patent_no'])
        self.assertEqual(data['patent_use_code'], response['patent_use_code'])

    @parameterized.expand([
        'appl_type',
        'appl_no',
        'product_no',
        'patent_no',
        'patent_use_code',
    ])
    def test_read_validation_error_blank(self, field_name):
        self.assertRaises(
            ValidationError,
            self.inst.read,
            {field_name: ''},
        )

    def test_read_all(self):
        response = self.inst.read({})
        self.assertEqual(len(response), 1)

    @parameterized.expand([
        ('appl_no', 1),
        ('product_no', 2),
        ('patent_no', 1),
    ])
    def test_read_w_params(self, field_name, expected_length):
        # setup
        new_ob_patent = self.inst.create({
            'appl_no': '22102',
            'appl_type': 'N',
            'delist_flag': '',
            'drug_product_flag': '',
            'drug_substance_flag': '',
            'patent_expire_date': 'Oct 30, 2009',
            'patent_no': '6428810',
            'patent_use_code': 'U-659',
            'product_no': '1',
            'submission_date': ''
        })

        response = self.inst.read({})
        self.assertEqual(len(response), 2)

        response = self.inst.read({field_name: new_ob_patent[field_name]})
        self.assertEqual(expected_length, len(response))

    def test_read_w_appl_nos(self):
        # setup
        new_ob_patent = self.inst.create({
            'appl_no': '22102',
            'appl_type': 'N',
            'delist_flag': '',
            'drug_product_flag': '',
            'drug_substance_flag': '',
            'patent_expire_date': 'Oct 30, 2009',
            'patent_no': '6428810',
            'patent_use_code': 'U-659',
            'product_no': '1',
            'submission_date': ''
        })

        response = self.inst.read({})
        self.assertEqual(len(response), 2)
        response = self.inst.read({'appl_nos': [new_ob_patent['appl_no'], 2]})
        self.assertEqual(1, len(response))
        self.assertIn(new_ob_patent, response)

        response = self.inst.read({'appl_nos': []})
        self.assertEqual(0, len(response))

    def test_update_not_found(self):
        invalid_id = 99999
        args = []
        kwargs = {'id': invalid_id, 'params': {
            'appl_no': '22101',
            'appl_type': 'N',
            'delist_flag': '',
            'drug_product_flag': '',
            'drug_substance_flag': '',
            'patent_expire_date': 'Oct 30, 2009',
            'patent_no': '6428810*PED',
            'patent_use_code': 'U-786',
            'product_no': '1',
            'submission_date': ''
        }}
        self.assertRaises(
            OrangeBookPatentNotFoundException,
            self.inst.update,
            *args,
            **kwargs
        )

    @parameterized.expand([
        'product_no',
        'patent_no',
        'patent_use_code',
    ])
    def test_update_validation_error_blank(self, field_name):
        args = []
        kwargs = {
            'id': self.ob_patent1['id'],
            'params': {
                'appl_no': '',
                'appl_type': 'N',
                'delist_flag': '',
                'drug_product_flag': '',
                'drug_substance_flag': '',
                'patent_expire_date': 'Oct 30, 2009',
                'patent_no': '6428810',
                'patent_use_code': '',
                'product_no': '123',
                'submission_date': ''
            },
        }
        kwargs['params'][field_name] = ''
        self.assertRaises(
            ValidationError,
            self.inst.update,
            *args,
            **kwargs
        )

    def test_update(self):
        new_data = {
            'appl_no': '22103',
            'appl_type': 'NN',
            'delist_flag': '',
            'drug_product_flag': '',
            'drug_substance_flag': '',
            'patent_expire_date': 'Oct 30, 2009',
            'patent_no': '6428810*PED',
            'patent_use_code': 'U-789',
            'product_no': '12',
            'submission_date': ''
        }
        response = self.inst.update(
            id=self.ob_patent1['id'],
            params=new_data,
        )
        self.assertEqual(response['id'], self.ob_patent1['id'])
        self.assertEqual(
            response['appl_no'],
            new_data['appl_no'],
        )
        self.assertEqual(
            response['product_no'],
            new_data['product_no'],
        )
        self.assertEqual(
            response['appl_type'],
            new_data['appl_type'],
        )

    def test_update_partial(self):
        new_data = {
            'appl_no': '123',
            'appl_type': 'NM',
            'patent_expire_date': '',
            'product_no': '0123123',
        }
        response = self.inst.update(
            id=self.ob_patent1['id'],
            params=new_data,
        )
        self.assertEqual(response['id'], self.ob_patent1['id'])
        self.assertEqual(
            response['appl_no'],
            new_data['appl_no'],
        )
        self.assertEqual(
            response['appl_type'],
            new_data['appl_type'],
        )
        self.assertEqual(
            response['product_no'],
            new_data['product_no'],
        )
        self.assertIsNone(response['patent_expire_date'])
