# -*- coding: utf-8 -*-
from odoo import fields, models, _

class VhConfigSettings(models.TransientModel):
  _inherit = 'res.config.settings'

  # MAIL TEMPLATES
  order_item_mail_template_id = fields.Many2one(
    related='company_id.order_item_mail_template_id',
    string=_("Order item notification template"),
    readonly=False)
