from ..sc_test_case import SCTestCase
from mock import Mock, patch
from datetime import date


class TestContractCompensationWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env['contract.contract']
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.partner = self.browse_ref('base.partner_demo')
        partner_id = self.partner.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        product_ref = self.browse_ref('somconnexio.Fibra100Mb')
        self.product = self.env["product.product"].search(
            [('default_code', '=', product_ref.default_code)]
        )
        contract_line = {
            "name": self.product.name,
            "product_id": self.product.id,
            "date_start": "2020-01-01 00:00:00"
        }
        vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_vodafone"
            ),
            'vodafone_fiber_service_contract_info_id': (
                self.vodafone_fiber_contract_service_info.id
            ),
            'bank_id': self.partner.bank_ids.id,
            'contract_line_ids': [(0, 0, contract_line)],
        }
        self.contract = self.env['contract.contract'].create(vals_contract)
        self.pricelist_item = self.env["product.pricelist.item"].search(
            [('product_id', '=', self.product.id)]
        )
        self.price = self.pricelist_item.fixed_price
        self.days_without_service = 2.0
        self.tax = self.env['account.tax'].search([
            ('name', '=', 'IVA 21% (Servicios)')
        ])
        self.tax.code = 'TAX_HIGH'

    def test_compensate_exact_amount(self):
        wizard = self.env['contract.compensation.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'contract_ids': [(6, 0, [self.contract.id])],
            'partner_id': self.partner.id,
            'type': 'exact_amount',
            'exact_amount': self.days_without_service
        })
        ctx = wizard.button_compensate()['context']
        self.assertEquals(
            ctx['default_summary'],
            "The amount to compensate is %.2f €" % self.days_without_service
        )
        self.assertEquals(
            ctx['default_activity_type_id'],
            self.ref('somconnexio.mail_activity_type_sc_compensation')
        )
        self.assertEquals(
            ctx['default_res_id'],
            self.contract.id
        )
        self.assertEquals(
            ctx['default_res_model_id'],
            self.ref('contract.model_contract_contract')
        )

    def test_compensate_days_without_service_terminated_contract(self):
        self.contract.is_terminated = True
        wizard = self.env['contract.compensation.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'contract_ids': [(6, 0, [self.contract.id])],
            'partner_id': self.partner.id,
            'type': 'days_without_service',
            'days_without_service': self.days_without_service
        })
        ctx = wizard.button_compensate()['context']
        self.assertEquals(
            ctx['default_summary'],
            "The amount to compensate is %.2f €" % (
                self.price/30.0*self.days_without_service
            )
        )
        self.assertEquals(
            ctx['default_activity_type_id'],
            self.ref('somconnexio.mail_activity_type_sc_compensation')
        )
        self.assertEquals(
            ctx['default_res_id'],
            self.contract.id
        )
        self.assertEquals(
            ctx['default_res_model_id'],
            self.ref('contract.model_contract_contract')
        )

    @patch(
        'odoo.addons.somconnexio.wizards.contract_compensation.contract_compensation.SubscriptionService', # noqa
        return_value=Mock(spec=['create_one_shot'])
    )
    def test_compensate_days_without_service_active_contract(self, SubscriptionService):
        amount_to_compensate = round(
            (self.days_without_service * self.price / 30)
            , 4
        )
        create_one_shot = SubscriptionService.return_value.create_one_shot
        wizard = self.env['contract.compensation.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'contract_ids': [(6, 0, [self.contract.id])],
            'partner_id': self.partner.id,
            'type': 'days_without_service',
            'days_without_service': self.days_without_service
        })
        wizard.button_compensate()
        self.assertEquals(
            round(wizard.days_without_service_import, 4), amount_to_compensate
        )
        wizard.description = 'Test description'
        wizard.operation_date = date(2021, 5, 15)
        wizard.opencell_compensate()
        create_one_shot.assert_called_once_with(
            'CH_SC_OSO_COMPENSATION', -amount_to_compensate,
            description="Test description", operation_date=date(2021, 5, 15)

        )
