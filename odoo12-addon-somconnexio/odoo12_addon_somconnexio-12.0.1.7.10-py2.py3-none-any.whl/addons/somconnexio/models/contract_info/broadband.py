from odoo import models, fields


class BroadbandServiceContractInfo(models.Model):
    _name = 'broadband.service.contract.info'
    _inherit = 'base.service.contract.info'
    id_order = fields.Char('Order Id')
    previous_id = fields.Char('Previous Id')


class VodafoneFiberServiceContractInfo(models.Model):
    _name = 'vodafone.fiber.service.contract.info'
    _inherit = 'broadband.service.contract.info'
    vodafone_id = fields.Char('Vodafone ID', required=True)
    vodafone_offer_code = fields.Char('Vodafone Offer Code', required=True)
    contract_ids = fields.One2many(
        'contract.contract',
        'vodafone_fiber_service_contract_info_id',
        'Contracts'
    )


class Router4GServiceContractInfo(models.Model):
    _name = 'router.4g.service.contract.info'
    _inherit = 'vodafone.fiber.service.contract.info'
    phone_number = fields.Char(default='-')


class MMFiberServiceContractInfo(models.Model):
    _name = 'mm.fiber.service.contract.info'
    _inherit = 'broadband.service.contract.info'
    mm_id = fields.Char('MásMóvil ID', required=True)
    contract_ids = fields.One2many(
        'contract.contract',
        'mm_fiber_service_contract_info_id',
        'Contracts'
    )


class OrangeFiberServiceContractInfo(models.Model):
    _name = 'orange.fiber.service.contract.info'
    _inherit = 'broadband.service.contract.info'
    suma_id = fields.Char('Suma ID', required=True)
    contract_ids = fields.One2many(
        'contract.contract',
        'orange_fiber_service_contract_info_id',
        'Contracts'
    )
    phone_number = fields.Char(default='-')


class ADSLServiceContractInfo(models.Model):
    _name = 'adsl.service.contract.info'
    _inherit = 'broadband.service.contract.info'
    administrative_number = fields.Char('Administrative Number', required=True)
    router_product_id = fields.Many2one(
        'product.product', 'Router Model', required=True
    )
    router_lot_id = fields.Many2one(
        'stock.production.lot', 'S/N / MAC Address', required=True
    )
    ppp_user = fields.Char(required=True)
    ppp_password = fields.Char(required=True)
    endpoint_user = fields.Char(required=True)
    endpoint_password = fields.Char(required=True)
    contract_ids = fields.One2many(
        'contract.contract',
        'adsl_service_contract_info_id',
        'Contracts'
    )


class XOLNFiberServiceContractInfo(models.Model):
    _name = 'xoln.fiber.service.contract.info'
    _inherit = 'broadband.service.contract.info'
    external_id = fields.Char('External ID', required=True)
    project = fields.Selection(
        [('laBorda', 'La Borda'), ('xGreta', 'Xarxa Greta')],
        'Project', required=True
    )
    router_product_id = fields.Many2one(
        'product.product', 'Router Model', required=True
    )
    router_lot_id = fields.Many2one(
        'stock.production.lot', 'S/N / MAC Address', required=True
    )
    contract_ids = fields.One2many(
        'contract.contract',
        'xoln_fiber_service_contract_info_id',
        'Contracts'
    )
