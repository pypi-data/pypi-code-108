from odoo import models, fields


class OperationRequest(models.Model):
    _inherit = 'operation.request'

    termination_reason = fields.Many2one(
        'operation.request.terminate.reason',
        string='Termination Reason'
    )

    termination_considerations = fields.Char(
        string='Termination Considerations'
    )
