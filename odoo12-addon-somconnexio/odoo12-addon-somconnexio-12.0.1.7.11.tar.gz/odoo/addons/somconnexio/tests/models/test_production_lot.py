from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError
import odoo


class TestStockProductionLot(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.product_id = self.ref('stock.product_cable_management_box')

    def test_valid_mac_address(self):
        mac_address = '12:34:56:78:9A:BC'
        stock_production_lot = self.env['stock.production.lot'].create({
            'name': "abc",
            'product_id': self.product_id,
            'router_mac_address': mac_address
        })
        self.assertEquals(
            stock_production_lot.router_mac_address,
            mac_address
        )

    def test_invalid_mac_address(self):
        mac_address = '12:34:56:78:9A:BX'
        self.assertRaises(
            ValidationError,
            self.env['stock.production.lot'].create,
            [{
                'name': "abc",
                'product_id': self.product_id,
                'router_mac_address': mac_address

            }]
        )

    def test_lot_name_get(self):
        mac_address = '12:34:56:78:9A:BC'
        stock_production_lot = self.env['stock.production.lot'].create({
            'name': "abc",
            'product_id': self.product_id,
            'router_mac_address': mac_address
        })
        self.assertEquals(
            stock_production_lot.name_get(),
            [(stock_production_lot.id, 'abc / '+mac_address)]
        )
        stock_production_lot = self.env['stock.production.lot'].create({
            'name': "def",
            'product_id': self.product_id,
        })
        self.assertEquals(
            stock_production_lot.name_get(),
            [(stock_production_lot.id, 'def')]
        )

    def test_upper_mac_address(self):
        mac_address = 'aa:aa:aa:aa:aa:ff'
        stock_production_lot = self.env['stock.production.lot'].create({
            'name': "abc",
            'product_id': self.product_id,
            'router_mac_address': mac_address
        })
        self.assertEquals(
            stock_production_lot.router_mac_address,
            mac_address.upper()
        )
        stock_production_lot.write({'router_mac_address': mac_address})
        self.assertEquals(
            stock_production_lot.router_mac_address,
            mac_address.upper()
        )

    @odoo.tools.mute_logger("odoo.sql_db")
    def test_unique_mac_address(self):
        mac_address = 'aa:aa:aa:aa:aa:ff'
        self.env['stock.production.lot'].create({
            'name': "vvv",
            'product_id': self.product_id,
            'router_mac_address': mac_address
        })
        stock_production_lot = self.env['stock.production.lot'].create(
            {
                'name': "def",
                'product_id': self.product_id,
                'router_mac_address': mac_address

            }
        )
        self.assertTrue(stock_production_lot)
