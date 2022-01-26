from odoo import models, fields


class FiberSignalType(models.Model):
    _name = 'fiber.signal.type'
    code = fields.Char()
    name = fields.Char('Name', translate=True)
