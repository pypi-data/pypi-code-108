from odoo import fields, models, _


class AgedPartnerBalanceWizard(models.TransientModel):
    _inherit = 'aged.partner.balance.wizard'
    group_by_select = fields.Selection([
        ('account', _('Account')),
        ('partner', _('Partner')),
    ], 'Group by', default='account')

    def _prepare_report_aged_partner_balance(self):
        self.ensure_one()
        ret = super()._prepare_report_aged_partner_balance()
        ret['group_by_select'] = self.group_by_select
        return ret
