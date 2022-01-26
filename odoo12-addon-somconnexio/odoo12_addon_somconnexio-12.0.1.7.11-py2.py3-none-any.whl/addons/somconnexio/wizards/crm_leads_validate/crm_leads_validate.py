from odoo import api, fields, models


class CRMLeadsValidateWizard(models.TransientModel):
    _name = 'crm.lead.validate.wizard'
    crm_lead_ids = fields.Many2many('crm.lead')

    @api.multi
    def button_validate(self):
        self.ensure_one()
        self.crm_lead_ids.action_set_won()
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        crm_lead_ids = self.env.context['active_ids']
        defaults['crm_lead_ids'] = crm_lead_ids
        return defaults
