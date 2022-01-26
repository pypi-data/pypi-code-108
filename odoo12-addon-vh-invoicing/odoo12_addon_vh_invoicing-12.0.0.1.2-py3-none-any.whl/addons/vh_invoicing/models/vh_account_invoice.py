from odoo import models, fields, api
from odoo.tools.translate import _

class VhAccountInvoice(models.Model):
  _inherit = 'account.invoice'

  journal_xml_ref = fields.Char(string=_("Journal ref"), compute="_get_journal_xml_ref",store=False)
  order_item_id = fields.Many2one('vh.invoicing.order.item',string=_("Order item"))

  @api.depends('journal_id')
  def _get_journal_xml_ref(self):
    for record in self:
      ir_model_data = self.env['ir.model.data'].search([('model','=','account.journal'),('res_id','=',record.journal_id.id)])
      if ir_model_data.exists():
        record.journal_xml_ref = ir_model_data.name


