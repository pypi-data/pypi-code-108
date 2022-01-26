from odoo import models, fields


class OperationRequestTerminateReason(models.Model):
    _name = 'operation.request.terminate.reason'
    _description = 'Operation Request Terminate Reason'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
