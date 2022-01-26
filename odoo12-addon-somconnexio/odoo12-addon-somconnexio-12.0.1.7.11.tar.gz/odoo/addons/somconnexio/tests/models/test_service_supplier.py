from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class ServiceSupplierTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        self.partner = self.browse_ref('base.partner_demo')
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
        self.mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'icc': '123'
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
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.router_4G_contract_service_info = self.env[
            'router.4g.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.mm_fiber_contract_service_info = self.env[
            'mm.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'mm_id': '123',
        })
        self.contract_adsl_args = {
            'name': 'Contract w/service technology to adsl',
            'service_technology_id': self.ref(
                'somconnexio.service_technology_adsl'
            ),
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_jazztel'
            ),
            'adsl_service_contract_info_id': (
                self.adsl_contract_service_info.id
            ),
            'partner_id': self.partner.id,
            'service_partner_id': self.partner.id,
            'invoice_partner_id': self.partner.id,
            'bank_id': self.partner.bank_ids[0].id,
        }
        self.contract_mobile_args = {
            'name': 'Contract w/category contract to mobile '
                    'and w/o service technology',
            'service_technology_id': self.ref(
                'somconnexio.service_technology_mobile'
            ),
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_masmovil'
            ),
            'mobile_contract_service_info_id': (
                self.mobile_contract_service_info.id
            ),
            'partner_id': self.partner.id,
            'service_partner_id': self.partner.id,
            'invoice_partner_id': self.partner.id,
            'bank_id': self.partner.bank_ids[0].id,
        }
        self.contract_fiber_args = {
            'name': 'Contract w/service technology to fiber',
            'service_technology_id': self.ref(
                'somconnexio.service_technology_fiber'
            ),
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_vodafone'
            ),
            'vodafone_fiber_service_contract_info_id': (
                self.vodafone_fiber_contract_service_info.id
            ),
            'partner_id': self.partner.id,
            'service_partner_id': self.partner.id,
            'invoice_partner_id': self.partner.id,
            'bank_id': self.partner.bank_ids[0].id,
        }
        self.contract_router_4G_args = {
            'name': 'contract with router 4G technology',
            'service_technology_id': self.ref(
                'somconnexio.service_technology_4G'
            ),
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_vodafone'
            ),
            'router_4G_service_contract_info_id': (
                self.router_4G_contract_service_info.id
            ),
            'partner_id': self.partner.id,
            'service_partner_id': self.partner.id,
            'invoice_partner_id': self.partner.id,
            'contract_line_ids': []
        }

        self.xoln_fiber_contract_service_info = self.env[
            'xoln.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'external_id': '123',
            'id_order': '456',
            'project': 'laBorda',
            'router_product_id': self.router_product.id,
            'router_lot_id': self.router_lot.id,
        })
        return result

    def test_wrong_adsl_vodafone(self):
        contract_adsl_args = self.contract_adsl_args.copy()
        contract_adsl_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_vodafone'
            )
        })
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [contract_adsl_args]
        )

    def test_wrong_adsl_masmovil(self):
        contract_adsl_args = self.contract_adsl_args.copy()
        contract_adsl_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_masmovil'
            )
        })
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [contract_adsl_args]
        )

    def test_right_adsl_jazztel(self):
        contract_adsl_args = self.contract_adsl_args.copy()
        contract_adsl_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_jazztel'
            )
        })
        self.assertTrue(self.env['contract.contract'].create(
            contract_adsl_args
        ))

    def test_right_fiber_vodafone(self):
        contract_fiber_args = self.contract_fiber_args.copy()
        contract_fiber_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_vodafone'
            )
        })
        self.assertTrue(self.env['contract.contract'].create(
            contract_fiber_args
        ))

    def test_right_router_4G_vodafone(self):
        contract_router_4G_args = self.contract_router_4G_args.copy()
        contract_router_4G_args.update({
            'service_supplier_id': self.ref('somconnexio.service_supplier_vodafone'),
        })
        self.assertTrue(self.env['contract.contract'].create(
            contract_router_4G_args
        ))

    def test_wrong_router_4G_masmovil(self):
        contract_router_4G_args = self.contract_router_4G_args.copy()
        contract_router_4G_args.update({
            'service_supplier_id': self.ref('somconnexio.service_supplier_masmovil'),
        })
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [contract_router_4G_args]
        )

    def test_wrong_fiber_masmovil(self):
        contract_fiber_args = self.contract_fiber_args.copy()
        contract_fiber_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_masmovil'
            )
        })
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [contract_fiber_args]
        )

    def test_right_fiber_mm(self):
        contract_fiber_args = self.contract_fiber_args.copy()
        contract_fiber_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_masmovil'
            ),
            'mm_fiber_service_contract_info_id': (
                self.mm_fiber_contract_service_info.id
            )
        })
        self.assertTrue(self.env['contract.contract'].create(
            contract_fiber_args
        ))

    def test_wrong_mobile_vodafone(self):
        contract_mobile_args = self.contract_mobile_args.copy()
        contract_mobile_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_vodafone'
            )
        })
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [contract_mobile_args]
        )

    def test_wrong_mobile_jazztel(self):
        contract_mobile_args = self.contract_mobile_args.copy()
        contract_mobile_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_jazztel'
            )
        })
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [contract_mobile_args]
        )

    def test_right_mobile_masmovil(self):
        contract_mobile_args = self.contract_mobile_args.copy()
        contract_mobile_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_masmovil'
            )
        })
        self.assertTrue(self.env['contract.contract'].create(
            contract_mobile_args
        ))

    def test_right_fiber_xoln(self):
        contract_fiber_args = self.contract_fiber_args.copy()
        contract_fiber_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_xoln'
            ),
            'xoln_fiber_service_contract_info_id': (
                self.xoln_fiber_contract_service_info.id
            )
        })
        self.assertTrue(self.env['contract.contract'].create(
            contract_fiber_args
        ))

    def test_wrong_adsl_xoln(self):
        contract_adsl_args = self.contract_adsl_args.copy()
        contract_adsl_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_xoln'
            )
        })
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [contract_adsl_args]
        )

    def test_wrong_fiber_xoln(self):
        contract_fiber_args = self.contract_fiber_args.copy()
        contract_fiber_args.update({
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_xoln'
            )
        })
        self.assertRaises(
            ValidationError,
            self.env['contract.contract'].create,
            [contract_fiber_args]
        )
