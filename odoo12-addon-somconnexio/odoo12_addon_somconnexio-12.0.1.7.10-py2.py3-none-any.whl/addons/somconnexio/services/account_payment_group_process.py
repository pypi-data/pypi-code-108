from odoo import _
from odoo.exceptions import UserError


class AccountPaymentGroupProcess():

    def __init__(self, env):
        self.env = env

    def process_payment_group(self, group_reference, raw_payment_group_lines):
        # Get data from the CSV
        payment_group_vals = {
            'payment_mode_id': self.env.ref('somconnexio.payment_mode_inbound_sepa').id,
            'journal_id': self.env.ref('somconnexio.payment_mode_inbound_sepa').id,
            'company_partner_bank_id': self.env.ref(
                'base.main_company'
            ).partner_id.bank_ids[0].id,
            'payment_type': 'inbound',
            'description': group_reference,
            'company_id': self.env.ref('base.main_company').id,
        }
        payment_order = self.env['account.payment.order'].create(payment_group_vals)
        for row in raw_payment_group_lines:
            partner = self._get_partner(row['Titulars/ID'])
            partner_bank = self._get_partner_bank(partner, row['Números/Número'])
            mandate = self._get_partner_bank_mandate(partner, partner_bank)

            payment_line_vals = {
                'partner_id': partner.id,
                'partner_bank_id': partner_bank.id,
                'mandate_id': mandate.id,
                'currency_id': self.env.ref('base.EUR').id,
                'communication_type': 'normal',
                'communication': row['Pagaments/Descripció'],
                'amount_currency': row['Pagaments/Import'],
                'date': row['Pagaments/Data'],
                'company_id': mandate.company_id.id,
                'order_id': payment_order.id,
            }
            self.env['account.payment.line'].create(
                payment_line_vals
            )

    def _get_partner(self, ref):
        partner = self.env['res.partner'].search(
            [('ref', '=', ref)]
        )
        if not partner:
            raise UserError(_("Partner with Reference {} not found.").format(ref))
        if len(partner) > 1:
            raise UserError(_("More than one partner with reference {}.").format(
                ref
            ))
        return partner[0]

    def _get_partner_bank(self, partner, iban):
        partner_bank = self.env['res.partner.bank'].search(
            [
                ('partner_id', '=', partner.id),
                ('acc_number', '=', iban)
            ], limit=1
        )
        if not partner_bank:
            raise UserError(_(
                "Bank account with IBAN {} and Partner Ref {} not found."
            ).format(iban, partner.ref,))
        return partner_bank[0]

    def _get_partner_bank_mandate(self, partner, partner_bank):
        mandate = self.env['account.banking.mandate'].search(
            [
                ('partner_id', '=', partner.id),
                ('partner_bank_id', '=', partner_bank.id)
            ], limit=1
        )
        if not mandate:
            raise UserError(_(
                "SEPA mandate for IBAN {} and Partner Ref {} not found."
            ).format(
                partner_bank.acc_number,
                partner.ref,
            ))
        return mandate[0]
