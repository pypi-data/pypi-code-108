# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class VhInvoicingOrderItem(models.Model):
  _name = 'vh.invoicing.order.item'
  _inherit = ['vh.model.sequence.mixin']
  _prefix = "ORDER-ITEM"
  name= fields.Char(_("Name"))
  partner_id = fields.Many2one('res.partner',string=_("Partner"))
  order_id = fields.Many2one('vh.invoicing.order',string=("Order"))
  invoice_ids = fields.One2many('account.invoice','order_item_id',string=_("Invoices"))
  total_invoiced = fields.Float(string=_("Total invoiced"),compute="_get_total_invoiced",store=False)
  company_id = fields.Many2one('res.company',string=_("System Company"),compute="_get_company_id",store=False)

  @api.depends('invoice_ids')
  def _get_total_invoiced(self):
    for record in self:
      total = 0
      for invoice in record.invoice_ids:
        total += invoice.amount_total
      record.total_invoiced = total

  def _get_company_id(self):
    for record in self:
      record.company_id = record.env.user.company_id.id