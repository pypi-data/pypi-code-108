from odoo import models, fields, api


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = 'account.payment.line.create'
    limit_enabled = fields.Boolean('Split in new payment orders?', default=True)
    limit = fields.Integer('Group maximum lines', default=1000)
    queue_enabled = fields.Boolean('Do it in background?', default=True)
    due_date_from = fields.Date(string="Due Date From")
    move_date_from = fields.Date(string="Move Date From")

    @api.multi
    def create_payment_lines(self):
        if self.limit_enabled and self.move_line_ids:
            move_line_pool = self.env['account.move.line']
            limit = self.limit
            num_groups = len(self.move_line_ids) // limit
            if len(self.move_line_ids) % limit:
                num_groups += 1
            g = self.move_line_ids[0:limit]
            if self.queue_enabled:
                move_line_pool.with_delay(
                    priority=30,
                    channel='root.invoicing',
                ).create_payment_line_from_move_line_queued(
                    g.ids, self.order_id.id
                )
            else:
                g.create_payment_line_from_move_line(
                    self.order_id
                )
            for g in [
                self.move_line_ids[n*limit:(n+1)*limit]
                for n in range(1, num_groups)
            ]:
                order_id = self.order_id.copy()
                if self.queue_enabled:
                    move_line_pool.with_delay(
                        priority=30,
                        channel='root.invoicing',
                    ).create_payment_line_from_move_line_queued(
                        g.ids, order_id.id
                    )
                else:
                    g.create_payment_line_from_move_line(order_id)
        else:
            super().create_payment_lines()
        return True

    @api.multi
    def _prepare_move_line_domain(self):
        domain = super()._prepare_move_line_domain()
        if self.date_type == 'due' and self.due_date and self.due_date_from:
            pos = next(i for i, e in enumerate(domain) if e[0] == 'date_maturity')
            # Delete old 'or' clause
            del domain[pos-1:pos+2]
            domain += [
                ('date_maturity', '<=', self.due_date),
                ('date_maturity', '>=', self.due_date_from)]
        elif self.date_type == 'move' and self.move_date_from:
            domain.append(('date', '>=', self.move_date_from))
        return domain
