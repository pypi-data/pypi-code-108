# -*- coding: utf-8 -*-
from odoo import fields, models, _

class VhInvoicingConfigSettings(models.TransientModel):
  _inherit = 'res.config.settings'

  default_vh_journal_ids = fields.Many2many(
    related='company_id.default_vh_journal_ids',
    string=_("Vh journals")
  )