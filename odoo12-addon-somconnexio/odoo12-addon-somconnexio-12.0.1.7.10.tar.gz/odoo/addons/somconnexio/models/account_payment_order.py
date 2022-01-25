from odoo import models, fields, api
from odoo.addons.queue_job.job import job


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    set_uploaded_job_ids = fields.Many2many(
        comodel_name='queue.job',
        column1='account_payment_order_id',
        column2='job_id',
        string="Set as Uploaded Jobs",
        copy=False,
    )

    @job
    def generated2uploaded_job(self):
        self.ensure_one()
        if self.state != 'generated':
            return
        self.generated2uploaded()

    @api.multi
    def _prepare_move_line_offsetting_account(
        self, amount_company_currency, amount_payment_currency, bank_lines
    ):
        vals = super()._prepare_move_line_offsetting_account(
            amount_company_currency, amount_payment_currency, bank_lines
        )
        if vals.get("account_id") == self.payment_mode_id.transfer_account_id.id:
            vals["partner_id"] = False
        return vals
