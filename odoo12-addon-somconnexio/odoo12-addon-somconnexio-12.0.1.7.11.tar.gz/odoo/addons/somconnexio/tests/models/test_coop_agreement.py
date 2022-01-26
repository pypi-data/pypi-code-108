from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class CoopAgreementTest(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        broadband_product_tmpl_args = {
            'name': 'ADSL 20Mb',
            'type': 'service',
            'categ_id': self.ref('somconnexio.broadband_adsl_service')
        }
        product_broadband_tmpl = self.env['product.template'].create(
            broadband_product_tmpl_args
        )
        self.product_broadband = product_broadband_tmpl.product_variant_id

        mobile_product_tmpl_args = {
            'name': 'Sense minutes',
            'type': 'service',
            'categ_id': self.ref('somconnexio.mobile_service')
        }
        product_mobile_tmpl = self.env['product.template'].create(
            mobile_product_tmpl_args
        )
        self.product_mobile = product_mobile_tmpl.product_variant_id

        CoopAgreement = self.env['coop.agreement']

        vals_coop_agreement_broadband = {
            'partner_id': self.ref("easy_my_coop.res_partner_cooperator_1_demo"),
            'products': [(6, 0, [product_broadband_tmpl.id])],
            'code': 'CODE1',
        }
        self.coop_agreement_broadband = CoopAgreement.create(
            vals_coop_agreement_broadband
        )
        vals_subscription = {
            'already_cooperator': False,
            'is_company': False,
            'firstname': 'Manuel',
            'lastname': 'Dublues Test',
            'email': 'manuel@demo-test.net',
            'ordered_parts': 1,
            'address': 'schaerbeekstraat',
            'city': 'Brussels',
            'zip_code': '1111',
            'country_id': 20,
            'date': datetime.now() - timedelta(days=12),
            'company_id': 1,
            'source': 'manual',
            'share_product_id': False,
            'lang': 'en_US',
            'sponsor_id': False,
            'iban': 'ES6020808687312159493841',
            'vat': '98100145Q',
        }
        vals_subscription_broadband = vals_subscription.copy()
        vals_subscription_broadband.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship_coop_agreement',
            'coop_agreement_id': self.coop_agreement_broadband.id,
        })
        subscription_broadband = self.env['subscription.request'].create(
            vals_subscription_broadband)
        subscription_broadband.validate_subscription_request()
        partner_broadband = subscription_broadband.partner_id
        self.router_product = self.env['product.product'].search(
            [
                ("default_code", "=", "NCDS224WTV"),
            ]
        )
        self.router_lot = self.env['stock.production.lot'].create({
            'product_id': self.router_product.id,
            'name': '123',
            'router_mac_address': '12:BB:CC:DD:EE:90'
        })
        self.adsl_contract_service_info = self.env[
            'adsl.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'administrative_number': '123',
            'router_product_id': self.router_product.id,
            'router_lot_id': self.router_lot.id,
            'ppp_user': 'ringo',
            'ppp_password': 'rango',
            'endpoint_user': 'user',
            'endpoint_password': 'password'
        })
        self.contract_broadband_args = {
            'name': 'Contract w/coop agreement that limits to broadband',
            'partner_id': partner_broadband.id,
            'invoice_partner_id': partner_broadband.id,
            'contract_line_ids': [(0, False, {
                'name': 'Broadband',
                'product_id': self.product_broadband.product_variant_id.id
            })],
            'service_technology_id': self.ref('somconnexio.service_technology_adsl'),
            'service_supplier_id': self.ref('somconnexio.service_supplier_jazztel'),
            'service_partner_id': partner_broadband.id,
            'adsl_service_contract_info_id': (
                self.adsl_contract_service_info.id
            ),
            'bank_id': partner_broadband.bank_ids[0].id
        }
        self.mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'icc': '123'
        })
        self.contract_mobile_args = {
            'name': 'Contract w/coop agreement that limits to broadband',
            'partner_id': partner_broadband.id,
            'invoice_partner_id': partner_broadband.id,
            'contract_line_ids': [(0, False, {
                'name': 'Mobile',
                'product_id': self.product_mobile.product_variant_id.id
            })],
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_masmovil'
            ),
            'service_technology_id': self.ref(
                'somconnexio.service_technology_mobile'
            ),
            'mobile_contract_service_info_id': (
                self.mobile_contract_service_info.id
            ),
            'bank_id': partner_broadband.bank_ids[0].id
        }

    def test_coop_agreement_right_product(self):
        self.assertTrue(
            self.env['contract.contract'].create(
                self.contract_broadband_args
            )
        )

    def test_coop_agreement_wrong_product(self):
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [self.contract_mobile_args]
        )
