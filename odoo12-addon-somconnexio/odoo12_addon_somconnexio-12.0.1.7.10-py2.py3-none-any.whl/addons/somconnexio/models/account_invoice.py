from odoo import models, fields, api
import json
from odoo.addons.queue_job.job import job
from odoo.addons.account_payment_partner.models.account_invoice import AccountInvoice as APPAccountInvoice # noqa
from ..services.account_invoice_process import AccountInvoiceProcess


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    oc_taxes = fields.Char()
    oc_total = fields.Float()
    oc_untaxed = fields.Float()
    oc_total_taxed = fields.Float()
    payment_mode_type = fields.Char(compute='_get_payment_mode_type')
    last_return_amount = fields.Float(compute='_get_last_return_amount')
    account_id = fields.Many2one(copy=True)

    @api.depends('payments_widget')
    def _get_last_return_amount(self):
        for inv in self:
            if inv.payments_widget != "false":
                last_returns = sorted([
                    e for e in json.loads(inv.payments_widget)['content']
                    if e.get('returned')
                ], key=lambda x: x['date'], reverse=True)
                inv.last_return_amount = (
                    bool(last_returns) and abs(last_returns[0]['amount'])
                )
            else:
                inv.last_return_amount = False

    @api.depends('type')
    def _get_payment_mode_type(self):
        for inv in self:
            if inv.type in ('out_invoice', 'in_refund'):
                inv.payment_mode_type = 'inbound'
            elif inv.type in ('out_refund', 'in_invoice'):
                inv.payment_mode_type = 'outbound'

    @job
    def create_invoice(self, **params):
        service = AccountInvoiceProcess(self.env)
        service.create(**params)

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount',
                 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'date')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        if self.oc_untaxed:
            self.amount_untaxed = self.oc_untaxed
        else:
            self.amount_untaxed = sum(
                line.price_subtotal for line in self.invoice_line_ids
            )
        if self.oc_total_taxed:
            self.amount_tax = self.oc_total_taxed
        else:
            self.amount_tax = sum(
                round_curr(line.amount_total) for line in self.tax_line_ids
            )
        if self.oc_total:
            self.amount_total = self.oc_total
        else:
            self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if (
            self.currency_id and self.company_id and
            self.currency_id != self.company_id.currency_id
        ):
            currency_id = self.currency_id
            rate_date = self._get_currency_rate_date() or fields.Date.today()
            amount_total_company_signed = currency_id._convert(
                self.amount_total, self.company_id.currency_id,
                self.company_id, rate_date
            )
            amount_untaxed_signed = currency_id._convert(
                self.amount_untaxed, self.company_id.currency_id,
                self.company_id, rate_date
            )
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    def compute_taxes(self):
        for invoice in self:
            oc_invoice = any([
                line.oc_amount_total
                for line in invoice.invoice_line_ids
            ])
            if not oc_invoice:
                super().compute_taxes()
                continue
            oc_taxes_parsed = json.loads(self.oc_taxes)
            for oc_tax in oc_taxes_parsed:
                taxes_amount = oc_tax['amountTax']
                base = oc_tax['amountWithoutTax']
                tax = self.env['account.tax'].search([
                    ('oc_code', '=', oc_tax['taxCode'])
                ])
                vals = {
                    'invoice_id': invoice.id,
                    'name': tax.name,
                    'tax_id': tax.id,
                    'amount': taxes_amount,
                    'base': base,
                    'manual': False,
                    'account_id': tax.account_id.id
                }
                self.env['account.invoice.tax'].create(vals)

    # TODO: Remove this code when a release of EasyMyCoop with:
    # https://github.com/coopiteasy/vertical-cooperative/pull/146
    def send_certificate_email(self, certificate_email_template, sub_reg_line):
        # we send the email with the certificate in attachment
        if self.company_id.send_certificate_email:
            certificate_email_template.sudo().send_mail(self.partner_id.id, False)

    @api.multi
    def get_invoice_pdf(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_invoice?invoice_number=%s' % self.name,
            'target': 'new',
        }

    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None, description=None,
            journal_id=None):
        vals = super(APPAccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        # vals['payment_mode_id'] = invoice.payment_mode_id.id
        if invoice.type == 'in_invoice':
            vals['partner_bank_id'] = invoice.partner_bank_id.id
        return vals

    def set_cooperator_effective(self, effective_date):
        if self.partner_id.share_ids.filtered(lambda rec: rec.share_number > 0):
            return True
        super(AccountInvoice, self).set_cooperator_effective(effective_date)
