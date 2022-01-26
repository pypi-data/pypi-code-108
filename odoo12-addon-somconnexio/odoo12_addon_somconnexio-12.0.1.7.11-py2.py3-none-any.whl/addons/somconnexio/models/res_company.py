from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # TODO: Remove this code when a release of EasyMyCoop with:
    # https://github.com/coopiteasy/vertical-cooperative/pull/146
    send_certificate_email = fields.Boolean(
        string="Send certificate email",
        default=True
    )
    # TODO: Remove this code when a release of EasyMyCoop with:
    # https://github.com/coopiteasy/vertical-cooperative/pull/146
    send_confirmation_email = fields.Boolean(
        string="Send confirmation email",
        default=True
    )
    # TODO: Remove this code when a release of EasyMyCoop with:
    # https://github.com/coopiteasy/vertical-cooperative/pull/146
    send_capital_release_email = fields.Boolean(
        string="Send Capital Release email",
        default=True
    )
