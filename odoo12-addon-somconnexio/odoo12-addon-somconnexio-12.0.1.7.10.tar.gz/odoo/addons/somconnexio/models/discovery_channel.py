from odoo import models, fields


class DiscoveryChannel(models.Model):
    _name = 'discovery.channel'
    name = fields.Char('Name', translate=True)
