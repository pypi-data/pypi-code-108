from odoo import models, fields


class PreviousProvider(models.Model):
    _name = 'previous.provider'
    name = fields.Char('Name')
    code = fields.Char('Code')
    mobile = fields.Boolean('Mobile')
    broadband = fields.Boolean('Broadband')
