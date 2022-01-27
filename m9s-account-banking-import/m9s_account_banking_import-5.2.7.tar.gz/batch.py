# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta


class BatchLine(metaclass=PoolMeta):
    __name__ = 'account.batch.line'

    bank_imp_line = fields.Many2One('banking.import.line',
        'Banking Import Line', readonly=True)

    @fields.depends('posting_text', 'contra_account', 'bank_imp_line')
    def on_change_contra_account(self):
        super().on_change_contra_account()
        if self.contra_account and not self.posting_text:
            self.posting_text = (self.bank_imp_line
                and self.bank_imp_line.contra_name)

    def _get_move_line(self, debit, credit, account, second_currency,
            amount_second_currency):
        line = super()._get_move_line(debit, credit, account, second_currency,
            amount_second_currency)
        line.origin = self.bank_imp_line
        return line
