from odoo import fields, models


class ContractTerminateUserReason(models.Model):

    _name = 'contract.terminate.user.reason'
    _description = 'Contract Termination User Reason'
    _order = "sequence"

    name = fields.Char(required=True)
    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer(string="Sequence")
