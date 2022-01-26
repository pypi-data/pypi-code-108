from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"
    name = fields.Char(translate=True)
