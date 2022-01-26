# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class VhCompany(models.Model):
  _inherit = 'res.company'

  default_vh_journal_ids = fields.Many2many('account.journal', 
    'vh_invoicing_company_account_journal', 'company_id', 'account_journal_id',string=_("Vh journals"))