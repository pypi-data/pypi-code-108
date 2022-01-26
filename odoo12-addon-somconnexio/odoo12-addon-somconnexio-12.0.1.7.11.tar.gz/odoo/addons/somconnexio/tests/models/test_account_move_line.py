from ..sc_test_case import SCTestCase
from mock import patch
import mock


class AccountMoveLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.move = self.env['account.move'].create({
            'journal_id': self.ref('somconnexio.caixa_guissona_journal'),
            'amount': 100.0,
            'name': 'BGUI/2021/001',
            'ref': 'Ordres de cobrament PAY0024'
        })
        self.move_line = self.env['account.move.line'].create({
            'move_id': self.move.id,
            'name': 'Línia L09692 de banc de cobrament',
            'account_id': self.env.ref('l10n_es.1_account_common_4300').id
        })

    def test_display_name_account_move_line(self):
        self.assertEquals(
            self.move_line.name_get(),
            [(self.move_line.id, '{}({})'.format(self.move.name, self.move_line.name))]
        )

    @patch('odoo.addons.account_banking_mandate.models.account_move_line.AccountMoveLine._prepare_payment_line_vals',  # noqa
           return_value={})
    def test_prepare_payment_line_vals_with_opencell_invoice(self, _):
        invoice = self.env['account.invoice'].create({
            'type': 'out_invoice',
            'name': 'SO2021-014530'
        })
        self.move_line.invoice_id = invoice
        self.move_line.journal_id = self.ref('somconnexio.consumption_invoices_journal')
        payment_line_vals = self.move_line._prepare_payment_line_vals(mock.ANY)
        self.assertIn('communication', payment_line_vals)
        self.assertEquals(payment_line_vals['communication'], invoice.name)

    @patch('odoo.addons.account_banking_mandate.models.account_move_line.AccountMoveLine._prepare_payment_line_vals',  # noqa
           return_value={'communication': 'RCON/2021/0019'})
    def test_prepare_payment_line_vals_with_opencell_invoice_refund(self, _):
        invoice = self.env['account.invoice'].create({
            'type': 'out_refund',
            'name': 'SO2021-014530'
        })
        self.move_line.invoice_id = invoice
        self.move_line.journal_id = self.ref('somconnexio.consumption_invoices_journal')
        payment_line_vals = self.move_line._prepare_payment_line_vals(mock.ANY)
        self.assertIn('communication', payment_line_vals)
        self.assertEquals(payment_line_vals['communication'], 'RCON/2021/0019')

    @patch('odoo.addons.account_banking_mandate.models.account_move_line.AccountMoveLine._prepare_payment_line_vals',  # noqa
           return_value={'communication': 'Ordres de cobrament PAY0024'})
    def test_prepare_payment_line_vals_without_invoice(self, _):
        payment_line_vals = self.move_line._prepare_payment_line_vals(mock.ANY)
        self.assertFalse(self.move_line.invoice_id)
        self.assertIn('communication', payment_line_vals)
        self.assertEquals(
            payment_line_vals['communication'], 'Ordres de cobrament PAY0024'
        )

    @patch('odoo.addons.account_banking_mandate.models.account_move_line.AccountMoveLine._prepare_payment_line_vals',  # noqa
           return_value={'communication': 'BGUI/2021/001'})
    def test_prepare_payment_line_vals_with_regular_invoice(self, _):
        invoice = self.env['account.invoice'].create({
            'type': 'out_invoice',
            'name': 'CBC09-000462015',
        })
        self.move_line.invoice_id = invoice
        payment_line_vals = self.move_line._prepare_payment_line_vals(mock.ANY)
        self.assertIn('communication', payment_line_vals)
        self.assertEquals(payment_line_vals['communication'], 'BGUI/2021/001')
