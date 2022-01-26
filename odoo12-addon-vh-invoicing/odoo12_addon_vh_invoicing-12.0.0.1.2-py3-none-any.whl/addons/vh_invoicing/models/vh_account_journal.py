# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class VhAccountJournal(models.Model):
  _inherit = 'account.journal'

  is_vh_journal = fields.Boolean(string=_("VH Journal"))

  order_mids = fields.Many2many('vh.invoicing.order', 
    'vh_invoicing_order_account_journal', 'account_journal_id',
    'invoicing_order_id',string=_("Account journals"))

  # vh_invoicing_config_settings_company_ids = fields.Many2many('res.company', 
  #   'vh_invoicing_company_account_journal', 'account_journal_id', 'company_id', string=_("Vh journals"))