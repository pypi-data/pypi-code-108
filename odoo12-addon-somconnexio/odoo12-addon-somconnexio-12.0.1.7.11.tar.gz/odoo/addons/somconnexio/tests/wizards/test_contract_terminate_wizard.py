from datetime import date
from ..sc_test_case import SCTestCase


class TestContractTerminateWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.masmovil_mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'icc': '123',
        })
        self.partner = self.browse_ref('base.partner_demo')
        partner_id = self.partner.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        product_ref = self.browse_ref('somconnexio.150Min1GB')
        product = self.env["product.product"].search(
            [('default_code', '=', product_ref.default_code)]
        )
        contract_line = {
            "name": product.name,
            "product_id": product.id,
            "date_start": "2020-01-01 00:00:00"
        }
        self.bank_b = self.env['res.partner.bank'].create({
            'acc_number': 'ES1720852066623456789011',
            'partner_id': partner_id
        })
        self.banking_mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': self.bank_b.id,
        })

        vals_contract = {
            'name': 'Test Contract One Shot Request',
            'partner_id': partner_id,
            'service_partner_id': service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_mobile"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mobile_contract_service_info_id': (
                self.masmovil_mobile_contract_service_info.id
            ),
            'mandate_id': self.banking_mandate.id,
            'contract_line_ids': [
                (0, False, contract_line)
            ]
        }
        self.contract = self.env['contract.contract'].create(vals_contract)

        self.terminate_reason = self.env['contract.terminate.reason'].create({
            'name': 'terminate_reason'
        })

        self.terminate_user_reason = self.env['contract.terminate.reason'].create({
            'name': 'terminate_user_reason'
        })

    def test_wizard_terminate_contract_user_reason(self):
        terminate_date = date.today()
        wizard = self.env['contract.terminate.wizard'].with_context(
            active_id=self.contract.id
        ).create({
            'terminate_date': terminate_date,
            'terminate_reason_id': self.terminate_reason.id,
            'terminate_user_reason_id': self.terminate_user_reason.id,
        })

        wizard.terminate_contract()
        self.assertTrue(self.contract.is_terminated)
        self.assertEqual(self.contract.terminate_date, terminate_date)
        self.assertEqual(
            self.contract.terminate_user_reason_id.id, self.terminate_user_reason.id
        )
        self.contract.action_cancel_contract_termination()
        self.assertFalse(self.contract.is_terminated)
        self.assertFalse(self.contract.terminate_reason_id)
        self.assertFalse(self.contract.terminate_user_reason_id)
