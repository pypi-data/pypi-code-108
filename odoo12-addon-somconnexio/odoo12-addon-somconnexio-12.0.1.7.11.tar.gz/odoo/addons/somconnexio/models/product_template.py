from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    catalog_attribute_id = fields.Many2one(
        'product.attribute.value', "Catalog Product Attribute Value"
    )
