from odoo import api, fields, models


class InvoiceClaim1SendWizard(models.TransientModel):
    _name = 'invoice.claim.1.send.wizard'
    invoice_ids = fields.Many2many('account.invoice')

    @api.multi
    def button_send(self):
        self.ensure_one()
        for invoice in self.invoice_ids:
            if invoice.journal_id == self.env.ref('somconnexio.subscription_journal'):
                invoice.activity_send_mail(
                    self.env.ref('somconnexio.invoice_claim_1_capital_template').id
                )
            else:
                invoice.activity_send_mail(
                    self.env.ref('somconnexio.invoice_claim_1_template').id
                )
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        mail_activity_ids = self.env.context['active_ids']
        mail_activity_pool = self.env['mail.activity']
        invoice_ids = [
            mail_activity_pool.browse(act_id).res_id
            for act_id in mail_activity_ids
        ]
        defaults['invoice_ids'] = invoice_ids
        return defaults
