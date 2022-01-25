from datetime import date

from ..sc_test_case import SCTestCase


class TestContractHolderChangeWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.partner = self.browse_ref('base.partner_demo')
        partner_id = self.partner.id
        self.service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service',
            'street': 'New test street'
        })
        contract_line = {
            "name": "Hola",
            "product_id": self.browse_ref('somconnexio.Fibra600Mb').id,
            "date_start": '2020-01-01'
        }
        vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': self.service_partner.id,
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

        self.partner_b = self.browse_ref('somconnexio.res_partner_2_demo')
        self.partner_b_bank = self.browse_ref('somconnexio.demo_bank_id')
        self.banking_mandate = self.env['account.banking.mandate'].create({
            'parent_id': self.partner_b.id,
            'partner_bank_id': self.partner_b_bank.id,
            'format': 'sepa',
            'type': 'recurrent',
            'company_id': 1,
            'unique_mandate_reference': 'BM0000003',
            'signature_date': '2021-04-12',
            'state': 'valid'
        })

    def test_wizard_holder_change_ok(self):
        group_can_terminate_contract = self.env.ref(
            "contract.can_terminate_contract"
        )
        group_can_terminate_contract.users |= self.env.user

        wizard = self.env['contract.holder.change.wizard'].with_context(
            active_id=self.contract.id
        ).create({
            'change_date': date.today(),
            'partner_id': self.partner_b.id,
            'invoice_partner_id': self.partner_b.id,
            'banking_mandate_id': self.banking_mandate.id
        })
        self.assertEqual(
            wizard.payment_mode,
            self.browse_ref('somconnexio.payment_mode_inbound_sepa')
        )
        self.assertEqual(
            wizard.available_banking_mandates,
            self.env['account.banking.mandate'].browse(self.banking_mandate.id)
        )
        new_service_partner_b = self.env['res.partner'].search([
            ('parent_id', '=', self.partner_b.id),
            ('type', '=', 'service'),
            ('street', '=', self.service_partner.street)
        ])
        self.assertFalse(new_service_partner_b)

        wizard.button_change()

        self.assertEqual(
            self.contract.terminate_reason_id,
            self.browse_ref('somconnexio.reason_holder_change')
        )

        self.assertEqual(
            self.contract.terminate_user_reason_id,
            self.browse_ref('somconnexio.user_reason_other')
        )

        self.assertTrue(self.contract.is_terminated)

        new_contract = self.env['contract.contract'].search([
            ('partner_id', '=', self.partner_b.id)
        ])

        self.assertEqual(
            self.contract.service_supplier_id,
            new_contract.service_supplier_id
        )
        self.assertEqual(
            self.contract.service_technology_id,
            new_contract.service_technology_id
        )
        self.assertEqual(
            self.contract.vodafone_fiber_service_contract_info_id,
            new_contract.vodafone_fiber_service_contract_info_id
        )
        self.assertEqual(
            self.contract.contract_line_ids[0].date_end,
            date.today()
        )
        self.assertEqual(
            new_contract.contract_line_ids[0].date_start,
            date.today()
        )
        self.assertEqual(
            new_contract.mandate_id,
            self.banking_mandate
        )

        new_service_partner_b = self.env['res.partner'].search([
            ('parent_id', '=', self.partner_b.id),
            ('type', '=', 'service'),
            ('street', '=', self.service_partner.street)
        ])
        self.assertTrue(new_service_partner_b)
        self.assertEqual(
            new_contract.service_partner_id.id, new_service_partner_b.id
        )

    def test_wizard_holder_change_service_address_already_existed(self):
        group_can_terminate_contract = self.env.ref(
            "contract.can_terminate_contract"
        )
        group_can_terminate_contract.users |= self.env.user

        wizard = self.env['contract.holder.change.wizard'].with_context(
            active_id=self.contract.id
        ).create({
            'change_date': date.today(),
            'partner_id': self.partner_b.id,
            'invoice_partner_id': self.partner_b.id,
            'banking_mandate_id': self.banking_mandate.id
        })

        new_service_partner_b = self.env['res.partner'].create({
            'parent_id': self.partner_b.id,
            'type': 'service',
            'street': self.service_partner.street
        })

        wizard.button_change()

        new_contract = self.env['contract.contract'].search([
            ('partner_id', '=', self.partner_b.id)
        ])

        self.assertEqual(
            new_contract.service_partner_id.id, new_service_partner_b.id
        )
