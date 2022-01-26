from ..sc_test_case import SCTestCase


class TestStockProductionLot(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.product2 = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'tracking': 'serial',
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.uom_unit = self.env.ref('uom.product_uom_unit')

    def test_onchange_valid_router_mac(self):
        move1 = self.env['stock.move'].create({
            'name': 'test_in_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_id': self.product2.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 2.0,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.write({'qty_done': 1.0})
        lot1_mac = 'AA:AA:AA:BB:BB:BB'
        lot2_mac = 'AA:AA:AA:CC:CC:CC'
        move1.move_line_ids[0].lot_name = 'lot1'
        move1.move_line_ids[0].lot_router_mac = lot1_mac
        self.assertFalse(move1.move_line_ids[0].onchange_router_mac())
        move1.move_line_ids[1].lot_name = 'lot2'
        move1.move_line_ids[1].lot_router_mac = lot2_mac
        self.assertFalse(move1.move_line_ids[0].onchange_router_mac())
        move1._action_done()
        self.assertEquals(
            move1.move_line_ids[0].lot_id.router_mac_address,
            lot1_mac
        )
        self.assertEquals(
            move1.move_line_ids[1].lot_id.router_mac_address,
            lot2_mac
        )

    def test_onchange_repeated_router_mac(self):
        picking = self.env['stock.picking'].create({
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })

        move1 = self.env['stock.move'].create({
            'name': 'test_in_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_id': self.product2.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 2.0,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'picking_id': picking.id
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.write({'qty_done': 1.0})
        lot1_mac = 'AA:AA:AA:BB:BB:BB'
        move1.move_line_ids[0].lot_name = 'lot1'
        move1.move_line_ids[0].lot_router_mac = lot1_mac
        move1.move_line_ids[0].picking_id = picking
        self.assertFalse(move1.move_line_ids[0].onchange_router_mac())
        move1.move_line_ids[1].lot_name = 'lot2'
        move1.move_line_ids[1].lot_router_mac = lot1_mac
        move1.move_line_ids[1].picking_id = picking
        move1.picking_id = picking
        res = move1.move_line_ids[1].onchange_router_mac()
        self.assertTrue(res)
        self.assertIn('warning', res)

    def test_onchange_invalid_router_mac(self):
        move1 = self.env['stock.move'].create({
            'name': 'test_in_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_id': self.product2.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids.write({'qty_done': 1.0})
        lot1_mac = 'AA:AA:AA:BB:BB:XX'
        move1.move_line_ids[0].lot_name = 'lot1'
        move1.move_line_ids[0].lot_router_mac = lot1_mac
        res = move1.move_line_ids[0].onchange_router_mac()
        self.assertTrue(res)
        self.assertIn('warning', res)

    def test_onchange_qty_1_router_mac(self):
        move1 = self.env['stock.move'].create({
            'name': 'test_in_1',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_id': self.product2.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })
        move1._action_confirm()
        move1._action_assign()
        lot1_mac = 'AA:AA:AA:BB:BB:XX'
        move1.move_line_ids[0].lot_router_mac = lot1_mac
        move1.move_line_ids[0].onchange_router_mac()
        self.assertEquals(move1.move_line_ids[0].qty_done, 1)
