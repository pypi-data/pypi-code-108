from odoo import api, fields, models
from odoo.tools.translate import _

class ModelSequenceMixin(models.AbstractModel):
  _name = "vh.model.sequence.mixin"
  _description = "Model Sequence Mixin"

  # do not access directly, always use get_api_external_id method
  name = fields.Char(string=_("Name"), index=True)
  external_id_sequence_id = fields.Many2one(
     comodel_name="ir.sequence",
     string="External ID Sequence",
     required=False,
  )

  @api.multi
  def _set_external_sequence(self):
    self.ensure_one()
    code = "%s.vh.model.sequence" % self._name
    Sequence = self.env["ir.sequence"]
    # check if code was created for that model
    sequence = Sequence.search([("code", "=", code)])
    if not sequence:
      sequence = Sequence.sudo().create({
        "name": code,
        "prefix": self._prefix+"-(%(range_year)s/%(month)s)-",
        "padding": 4,
        "code": code,
        "number_next": 1
      })

    self.sudo().write({"external_id_sequence_id": sequence.id})
    return True

  @api.constrains('name')
  def _set_name(self):
    for record in self:
      if not record.external_id_sequence_id:
        record._set_external_sequence()
        record.name = record.external_id_sequence_id._next()
