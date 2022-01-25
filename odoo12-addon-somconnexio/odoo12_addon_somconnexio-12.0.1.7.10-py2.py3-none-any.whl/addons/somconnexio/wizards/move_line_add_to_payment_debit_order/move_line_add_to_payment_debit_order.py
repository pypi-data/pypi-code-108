from odoo import models, api


class MoveLineAddToPaymentDebitOrder(models.TransientModel):
    _name = 'move.line.add.to.payment.debit.order'
    _description = 'Create payment lines from account move line tree view'

    @api.multi
    def run(self):
        self.ensure_one()
        assert self._context['active_model'] == 'account.move.line',\
            'Active model should be account.move.line'
        move_lines = self.env['account.move.line'].browse(
            self._context['active_ids'])
        action = move_lines.create_account_payment_line()
        return action
