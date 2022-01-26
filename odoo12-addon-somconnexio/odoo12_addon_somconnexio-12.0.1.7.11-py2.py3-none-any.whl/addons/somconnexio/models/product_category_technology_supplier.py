from odoo import models, fields


class ProductCategoryTechnologySupplier(models.Model):
    _name = 'product.category.technology.supplier'
    product_category_id = fields.Many2one('product.category', 'Product Category')
    service_supplier_id = fields.Many2one('service.supplier', 'Supplier')
    service_technology_id = fields.Many2one(
        'service.technology',
        'Technology'
    )
