from odoo import models, api


class AccountBankingMandate(models.Model):
    """SEPA Direct Debit Mandate"""
    _inherit = 'account.banking.mandate'

    def name_get(self):
        result = []
        for mandate in self:
            name = mandate.unique_mandate_reference
            acc_number = mandate.partner_bank_id.acc_number
            if acc_number:
                name = '{} [{}]'.format(name, acc_number)
            result.append((mandate.id, name))
        return result

    @api.multi
    @api.depends('unique_mandate_reference', 'partner_bank_id')
    def _compute_display_name2(self):
        for mandate in self:
            if mandate.format == 'sepa':
                mandate.display_name = '%s [%s]' % (
                    mandate.unique_mandate_reference,
                    mandate.partner_bank_id.acc_number)
            else:
                mandate.display_name = mandate.unique_mandate_reference
