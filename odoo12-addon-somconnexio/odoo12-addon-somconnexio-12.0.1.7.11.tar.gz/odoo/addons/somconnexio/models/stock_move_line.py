from odoo import fields, models, api
from collections import Counter
from odoo import _


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    lot_router_mac = fields.Char('Router MAC')

    def _get_similar_move_lines(self):
        self.ensure_one()
        lines = self.env['stock.move.line']
        picking_id = self.move_id.picking_id if self.move_id else self.picking_id
        if picking_id:
            lines |= picking_id.move_line_ids.filtered(
                lambda ml: ml.product_id == self.product_id and (
                    ml.lot_id or ml.lot_name or ml.lot_router_mac
                )
            )
        return lines

    @api.onchange('lot_router_mac')
    def onchange_router_mac(self):
        """ When the user is encoding a move line for a tracked product, we apply some logic to
        help him. This includes:
            - automatically switch `qty_done` to 1.0
            - warn if he has already encoded `lot_router_mac` in another move line
        """
        res = {}
        if self.product_id.tracking == 'serial':
            if not self.qty_done:
                self.qty_done = 1

            message = None
            if self.lot_router_mac:
                move_lines_to_check = self._get_similar_move_lines() - self
                if self.lot_router_mac:
                    counter = Counter(
                        [line.lot_router_mac.upper() for line in move_lines_to_check]
                    )
                    if (
                        not self.env['stock.production.lot'].check_mac_address(
                            self.lot_router_mac
                        )
                    ):
                        message = _(
                            'The MAC address is wrong.'
                        )
                    elif (
                        counter.get(self.lot_router_mac.upper()) and
                        counter[self.lot_router_mac.upper()] > 0
                    ):
                        message = _(
                            'You cannot use the same Router MAC twice. '
                            'Please correct the Router MACs encoded.'
                        )
            if message:
                res['warning'] = {'title': _('Warning'), 'message': message}
        return res

    def _action_done(self):
        super()._action_done()
        for ml in self:
            if ml.lot_id and ml.lot_router_mac:
                ml.lot_id.write({'router_mac_address': ml.lot_router_mac})
