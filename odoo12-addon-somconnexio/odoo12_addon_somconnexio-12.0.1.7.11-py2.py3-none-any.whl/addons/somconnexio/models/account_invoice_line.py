from odoo import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    oc_amount_untaxed = fields.Float()
    oc_amount_total = fields.Float()
    oc_amount_taxes = fields.Float()
    price_unit = fields.Float(required=False)
    quantity = fields.Float(required=False)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id',
                 'invoice_id.company_id', 'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(
                price, currency, self.quantity,
                product=self.product_id, partner=self.invoice_id.partner_id
            )
        if self.oc_amount_untaxed:
            self.price_subtotal = price_subtotal_signed = self.oc_amount_untaxed
        else:
            self.price_subtotal = price_subtotal_signed = (
                taxes['total_excluded'] if taxes else self.quantity * price
            )
        if self.oc_amount_total:
            self.price_total = self.oc_amount_total
        else:
            self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if (
            self.invoice_id.currency_id and
            self.invoice_id.currency_id != self.invoice_id.company_id.currency_id
        ):
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(
                price_subtotal_signed, self.invoice_id.company_id.currency_id,
                self.company_id or self.env.user.company_id, date or fields.Date.today()
            )
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    def _get_price_tax(self):
        for line in self:
            line.price_tax = (
                line.oc_amount_taxes
                if line.oc_amount_taxes
                else line.price_total - line.price_subtotal
            )
