from odoo import _, models, fields


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    _sql_constraints = [(
        'default_code_uniq',
        'unique (code)',
        _('The code must be unic')
        )]

    code = fields.Char("Code", required=True)
