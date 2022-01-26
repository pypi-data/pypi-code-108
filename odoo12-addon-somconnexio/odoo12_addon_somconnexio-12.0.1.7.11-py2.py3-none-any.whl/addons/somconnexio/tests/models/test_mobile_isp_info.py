from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class MobileISPInfoTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.mobile_isp_info_args = {
            'type': 'new',
        }

    def test_new_creation_ok(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()
        mobile_isp_info = self.env['mobile.isp.info'].create(
            mobile_isp_info_args_copy
        )
        self.assertTrue(mobile_isp_info.id)

    def test_portability_creation_ok(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()
        previous_provider_id = self.env['previous.provider'].browse(3)

        mobile_isp_info_args_copy.update({
            'type': 'portability',
            'icc_donor': '1234',
            'phone_number': '666666666',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider_id.id,
            'previous_owner_vat_number': '1234G',
            'previous_owner_name': 'Ford',
            'previous_owner_first_name': 'Windom',
        })

        mobile_isp_info = self.env['mobile.isp.info'].create(
            mobile_isp_info_args_copy
        )
        self.assertTrue(previous_provider_id.mobile)
        self.assertTrue(mobile_isp_info.id)

    def test_portability_creation_VAT_normalization(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()
        previous_provider_id = self.env['previous.provider'].browse(3)

        mobile_isp_info_args_copy.update({
            'type': 'portability',
            'icc_donor': '1234',
            'phone_number': '666666666',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider_id.id,
            'previous_owner_vat_number': '1234G',
            'previous_owner_name': 'Ford',
            'previous_owner_first_name': 'Windom',
        })

        mobile_isp_info = self.env['mobile.isp.info'].create(
            mobile_isp_info_args_copy
        )
        self.assertEqual(
            mobile_isp_info.previous_owner_vat_number,
            'ES1234G')

    def test_portability_wrong_previous_provider(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()
        previous_provider_id = self.env['previous.provider'].browse(57)

        mobile_isp_info_args_copy.update({
            'type': 'portability',
            'icc_donor': '1234',
            'phone_number': '666666666',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider_id.id,
            'previous_owner_vat_number': '1234G',
            'previous_owner_name': 'Ford',
            'previous_owner_first_name': 'Windom',
        })

        self.assertFalse(previous_provider_id.mobile)
        self.assertRaises(
            ValidationError,
            self.env['mobile.isp.info'].create,
            [mobile_isp_info_args_copy]
        )

    def test_portability_without_previous_provider(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()

        mobile_isp_info_args_copy.update({
            'type': 'portability',
            'icc_donor': '1234',
            'phone_number': '666666666',
            'previous_contract_type': 'contract',
            'previous_provider': None,
            'previous_owner_vat_number': '1234G',
            'previous_owner_name': 'Ford',
            'previous_owner_first_name': 'Windom',
        })

        self.assertRaises(
            ValidationError,
            self.env['mobile.isp.info'].create,
            [mobile_isp_info_args_copy]
        )

    def test_portability_without_previous_contract_type(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()

        mobile_isp_info_args_copy.update({
            'type': 'portability',
            'icc_donor': '1234',
            'phone_number': '666666666',
            'previous_contract_type': None,
            'previous_provider': self.ref('somconnexio.previousprovider3'),
            'previous_owner_vat_number': '1234G',
            'previous_owner_name': 'Ford',
            'previous_owner_first_name': 'Windom',
        })

        self.assertRaises(
            ValidationError,
            self.env['mobile.isp.info'].create,
            [mobile_isp_info_args_copy]
        )

    def test_portability_without_phone_number(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()

        mobile_isp_info_args_copy.update({
            'type': 'portability',
            'icc_donor': '1234',
            'phone_number': '',
            'previous_contract_type': 'contract',
            'previous_provider': self.ref('somconnexio.previousprovider3'),
            'previous_owner_vat_number': '1234g',
            'previous_owner_name': 'ford',
            'previous_owner_first_name': '',
        })

        self.assertRaises(
            ValidationError,
            self.env['mobile.isp.info'].create,
            [mobile_isp_info_args_copy]
        )

    def test_portability_prepaid_without_icc_donor(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()

        mobile_isp_info_args_copy.update({
            'type': 'portability',
            'icc_donor': '',
            'phone_number': '666666666',
            'previous_contract_type': 'prepaid',
            'previous_provider': self.ref('somconnexio.previousprovider3'),
            'previous_owner_vat_number': '1234g',
            'previous_owner_name': 'ford',
            'previous_owner_first_name': 'Hells',
        })

        self.assertRaises(
            ValidationError,
            self.env['mobile.isp.info'].create,
            [mobile_isp_info_args_copy]
        )

    def test_portability_contract_without_icc_donor(self):
        mobile_isp_info_args_copy = self.mobile_isp_info_args.copy()

        mobile_isp_info_args_copy.update({
            'type': 'portability',
            'icc_donor': '',
            'phone_number': '666666666',
            'previous_contract_type': 'contract',
            'previous_provider': self.ref('somconnexio.previousprovider3'),
            'previous_owner_vat_number': '1234g',
            'previous_owner_name': 'ford',
            'previous_owner_first_name': 'Hells',
        })

        mobile_isp_info = self.env['mobile.isp.info'].create(mobile_isp_info_args_copy)

        self.assertTrue(mobile_isp_info.id)
