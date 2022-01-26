from odoo import api, models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        if self.model == 'crm.lead.line':
            crm_lead = self.env['crm.lead.line'].browse(self.res_id).lead_id
            if crm_lead.partner_id:
                lang = crm_lead.partner_id.lang
            else:
                lang = crm_lead.subscription_request_id.lang
            ctx.update(lang=lang)
        values = self.with_context(ctx).onchange_template_id(
            self.template_id.id, self.composition_mode, self.model, self.res_id
        )['value']
        for fname, value in values.items():
            setattr(self, fname, value)
