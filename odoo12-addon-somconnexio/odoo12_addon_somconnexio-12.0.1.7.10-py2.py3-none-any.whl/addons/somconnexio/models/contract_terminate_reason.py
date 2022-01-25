from odoo import fields, models


class ContractTerminateReason(models.Model):
    _inherit = 'contract.terminate.reason'
    _order = "sequence"

    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer(string="Sequence")
