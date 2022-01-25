from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'
    oc_code = fields.Char('OC Code')
