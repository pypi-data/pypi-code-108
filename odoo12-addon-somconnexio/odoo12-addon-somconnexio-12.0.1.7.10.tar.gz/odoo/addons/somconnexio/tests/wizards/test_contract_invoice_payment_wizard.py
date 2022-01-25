from ..sc_test_case import SCTestCase
from datetime import date
import base64


class TestContractInvoicePaymentWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        partner = self.browse_ref('base.partner_demo')
        partner_id = partner.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': partner.bank_ids[0].id,
            'state': 'valid',
            'partner_id': partner.id,
            'signature_date': date(2021, 1, 1)
        })

        vals_contract = {
            'name': 'Test Contract Broadband',
            'code': '777',
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
                vodafone_fiber_contract_service_info.id
            ),
            'mandate_id': mandate.id,
            'payment_term_id': self.ref('account.account_payment_term'),
            'payment_term_mode': self.ref(
                'account_banking_sepa_direct_debit.payment_mode_inbound_sepa_dd1'
            )
        }
        vals_contract_2 = vals_contract.copy()
        vals_contract_2.update({
            'name': 'Test Contract Broadband 2',
            'code': '778',
        })
        self.contract = self.env['contract.contract'].create(vals_contract)
        self.contract_2 = self.env['contract.contract'].create(vals_contract_2)
        date_invoice = date(2021, 1, 31)
        self.invoice = self.env['account.invoice'].create({
            'partner_id': partner_id,
            'date_invoice': date_invoice,
            'name': 'SO_invoice_test'
        })
        self.invoice_2 = self.env['account.invoice'].create({
            'partner_id': partner_id,
            'date_invoice': date_invoice,
            'name': 'SO_invoice_test_2'
        })

    def test_import_invoice_payment_ok(self):
        csv = (
            'Invoice number,Subscription code\n'
            f'{self.invoice.name},{self.contract.code}'
        )
        data = base64.b64encode(csv.encode('utf-8'))
        wizard = self.env['contract.invoice.payment.wizard'].create(
            {'data': data}
        )
        wizard.run_wizard()
        self.assertFalse(wizard.errors)
        self.assertEquals(self.invoice.mandate_id, self.contract.mandate_id)
        self.assertEquals(self.invoice.payment_term_id, self.contract.payment_term_id)
        self.assertEquals(self.invoice.payment_mode_id, self.contract.payment_mode_id)

    def test_import_invoice_payment_not_found_contract(self):
        csv = (
            'Invoice number,Subscription code\n'
            f'{self.invoice_2.name},{self.contract_2.code}\n'
            f'{self.invoice.name},XXX'
        )
        data = base64.b64encode(csv.encode('utf-8'))
        wizard = self.env['contract.invoice.payment.wizard'].create(
            {'data': data}
        )
        wizard.run_wizard()
        self.assertTrue(wizard.errors)
        self.assertEquals(self.invoice_2.mandate_id, self.contract_2.mandate_id)
        self.assertEquals(
            self.invoice_2.payment_term_id, self.contract_2.payment_term_id
        )
        self.assertEquals(
            self.invoice_2.payment_mode_id, self.contract_2.payment_mode_id
        )

    def test_import_invoice_payment_not_found_invoice(self):
        csv = (
            'Invoice number,Subscription code\n'
            f'XXX,{self.contract.code}\n'
            f'{self.invoice_2.name},{self.contract_2.code}'
        )
        data = base64.b64encode(csv.encode('utf-8'))
        wizard = self.env['contract.invoice.payment.wizard'].create(
            {'data': data}
        )
        wizard.run_wizard()
        self.assertTrue(wizard.errors)
        self.assertEquals(self.invoice_2.mandate_id, self.contract_2.mandate_id)
        self.assertEquals(
            self.invoice_2.payment_term_id, self.contract_2.payment_term_id
        )
        self.assertEquals(
            self.invoice_2.payment_mode_id, self.contract_2.payment_mode_id
        )

    def test_import_invoice_payment_ignore_dup_contract(self):
        self.contract_2.code = self.contract.code
        csv = (
            'Invoice number,Subscription code\n'
            f'{self.invoice.name},{self.contract.code}'
        )
        data = base64.b64encode(csv.encode('utf-8'))
        wizard = self.env['contract.invoice.payment.wizard'].create(
            {'data': data}
        )
        wizard.run_wizard()
        self.assertFalse(wizard.errors)
        self.assertEquals(self.invoice.mandate_id, self.contract.mandate_id)
        self.assertEquals(self.invoice.payment_term_id, self.contract.payment_term_id)
        self.assertEquals(self.invoice.payment_mode_id, self.contract.payment_mode_id)
