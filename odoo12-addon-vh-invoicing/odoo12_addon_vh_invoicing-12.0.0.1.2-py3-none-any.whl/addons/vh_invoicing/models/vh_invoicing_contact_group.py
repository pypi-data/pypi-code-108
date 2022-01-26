# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class VhInvoicingContactGroup(models.Model):
  _name = 'vh.invoicing.contact.group'

  name= fields.Char(_("Name"))

  partner_mids = fields.Many2many('res.partner',
    'vh_partners_invoicing_contact_groups', 'invoicing_contact_group_id', 'partner_id',string=_("Related contacts"))