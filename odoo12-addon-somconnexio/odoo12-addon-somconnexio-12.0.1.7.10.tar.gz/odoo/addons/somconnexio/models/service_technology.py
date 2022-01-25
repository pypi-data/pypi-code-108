from odoo import models, fields


class ServiceTechnology(models.Model):
    _name = 'service.technology'
    name = fields.Char('Name')
