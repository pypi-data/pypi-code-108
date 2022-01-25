from odoo import models, api
from odoo.addons.queue_job.job import identity_exact


class PaymentOrderGeneratedToUploadedQueued(models.TransientModel):
    _name = 'payment.order.generated.uploaded.queued'
    _description = 'Mark as uploaded generated payment orders'

    @api.multi
    def run(self):
        self.ensure_one()
        queue_obj = self.env['queue.job']
        payment_orders = self.env['account.payment.order'].browse(
            self._context['active_ids'])
        for payment_order in payment_orders:
            new_delay = payment_order.with_delay(
                identity_key=identity_exact,
                channel='root.invoicing',
                priority=30
            ).generated2uploaded_job()
            job = queue_obj.search([('uuid', '=', new_delay.uuid)])
            payment_order.sudo().set_uploaded_job_ids = [(4, job.id)]
        return True
