from odoo import models, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.model
    def create(self, vals):
        new_res_partner_bank = super(ResPartnerBank, self).create(vals)

        if not new_res_partner_bank.bank_id:
            new_res_partner_bank._onchange_acc_number_base_bank_from_iban()

        return new_res_partner_bank
