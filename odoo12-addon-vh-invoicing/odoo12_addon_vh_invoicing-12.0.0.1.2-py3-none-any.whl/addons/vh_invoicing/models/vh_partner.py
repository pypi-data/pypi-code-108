from odoo import models, fields, api
from odoo.tools.translate import _

class VhPartner(models.Model):
  _inherit = 'res.partner'

  contact_group_mids = fields.Many2many('vh.invoicing.contact.group',
    'vh_partners_invoicing_contact_groups', 'partner_id', 'invoicing_contact_group_id',string=_("Invoicing Contact Groups"))