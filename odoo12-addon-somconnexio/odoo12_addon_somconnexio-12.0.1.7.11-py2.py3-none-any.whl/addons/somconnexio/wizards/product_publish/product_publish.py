from odoo import models, api, fields


class ProductPublish(models.TransientModel):
    _name = 'product.publish'
    _description = 'Mark a product as published in catalog'
    product_id = fields.Many2one('product.product')

    @api.multi
    def publish(self):
        self.product_id.public = True
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['product_id'] = self.env.context['active_id']
        return defaults


class ProductUnpublish(models.TransientModel):
    _name = 'product.unpublish'
    _description = 'Unmark a product as published in catalog'
    product_id = fields.Many2one('product.product')

    @api.multi
    def unpublish(self):
        self.product_id.public = False
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['product_id'] = self.env.context['active_id']
        return defaults
