from odoo import models, fields


class MobileServiceContractInfo(models.Model):
    _name = 'mobile.service.contract.info'
    _inherit = 'base.service.contract.info'
    icc = fields.Char("ICC", required=True)

    delivery_street = fields.Char(string='Delivery Street')
    delivery_street2 = fields.Char(string='Delivery Street 2')
    delivery_zip_code = fields.Char(string='Delivery ZIP')
    delivery_city = fields.Char(string='Delivery City')
    delivery_state_id = fields.Many2one(
        'res.country.state',
        string='Delivery State')
    delivery_country_id = fields.Many2one(
        'res.country',
        string='Delivery Country')
    contract_ids = fields.One2many(
        'contract.contract',
        'mobile_contract_service_info_id',
        'Contracts'
    )
