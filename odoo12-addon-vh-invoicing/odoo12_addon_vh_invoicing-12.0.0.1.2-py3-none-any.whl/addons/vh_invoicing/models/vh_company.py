# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class VhCompany(models.Model):
  _inherit = 'res.company'

  order_item_mail_template_id = fields.Many2one('mail.template',
    string=_("Order item notification template"))