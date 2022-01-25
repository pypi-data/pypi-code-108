from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from ...somoffice.user import SomOfficeUser


class PartnerCheckSomofficeEmail(models.TransientModel):
    _name = 'partner.check.somoffice.email.wizard'
    partner_id = fields.Many2one('res.partner')
    somoffice_email = fields.Char(
        string="Somoffice Email",
        compute="_compute_somoffice_email"
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['partner_id'] = self.env.context['active_id']
        return defaults

    @api.depends("partner_id")
    def _compute_somoffice_email(self):
        somoffice_user_info = SomOfficeUser.get(self.partner_id.vat)

        if somoffice_user_info.get("msg") in ["error", "User not found"]:
            msg = _("Couldn't reach SomOffice user. Please contact IT department")
            raise AccessError(msg)

        self.somoffice_email = somoffice_user_info.get('email')
