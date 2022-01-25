from odoo import models, fields


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    catalog_name = fields.Char("Catalog name")
