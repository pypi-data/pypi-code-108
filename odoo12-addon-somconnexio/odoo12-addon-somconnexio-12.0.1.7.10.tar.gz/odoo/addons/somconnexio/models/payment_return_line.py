from odoo import api, models, _
from odoo.exceptions import UserError


class PaymentReturnLine(models.Model):
    _inherit = "payment.return.line"

    @api.multi
    def _find_match(self):
        # we filter again to remove all ready matched lines in inheritance
        lines2match = self.filtered(lambda x: (
            (not x.move_line_ids) and x.reference))
        lines2match.match_invoice()

        lines2match = lines2match.filtered(lambda x: (
            (not x.move_line_ids) and x.reference))
        lines2match.match_move_lines()

        lines2match = lines2match.filtered(lambda x: (
            (not x.move_line_ids) and x.reference))
        lines2match.match_move()
        self._get_partner_from_move()
        self.filtered(lambda x: not x.amount)._compute_amount()

    @api.multi
    def match_invoice(self):
        for line in self:
            domain = line.partner_id and [
                ('partner_id', '=', line.partner_id.id)] or []
            domain.append(('number', '=', line.reference))
            invoice = self.env['account.invoice'].search(domain)
            if invoice:
                payments = invoice.payment_move_line_ids
                if line.return_id.journal_id:
                    payments = payments.filtered(
                        lambda x: x.journal_id == line.return_id.journal_id
                    )
                if payments:
                    line.move_line_ids = payments[0].ids
                    if not line.concept:
                        line.concept = _('Invoice: %s') % invoice.number

    @api.multi
    def match_move(self):
        for line in self:
            domain = line.partner_id and [
                ('partner_id', '=', line.partner_id.id)] or []
            domain.append(('name', '=', line.reference))
            if line.return_id.journal_id:
                domain.append(('journal_id', '=',
                               line.return_id.journal_id.id))
            move = self.env['account.move'].search(domain)
            if move:
                if len(move) > 1:
                    raise UserError(
                        _("More than one matches to move reference: %s") %
                        self.reference)
                line.move_line_ids = move.line_ids.filtered(lambda l: (
                    l.user_type_id.type == 'receivable' and l.reconciled
                )).ids
                if not line.concept:
                    line.concept = _('Move: %s') % move.ref

    @api.multi
    def match_move_lines(self):
        for line in self:
            domain = line.partner_id and [
                ('partner_id', '=', line.partner_id.id)] or []
            if line.return_id.journal_id:
                domain.append(('journal_id', '=',
                               line.return_id.journal_id.id))
            domain.extend([
                ('account_id.internal_type', '=', 'receivable'),
                ('reconciled', '=', True),
                '|',
                ('name', 'like', line.reference),
                ('ref', 'like', line.reference),
            ])
            move_lines = self.env['account.move.line'].search(domain)
            if move_lines:
                line.move_line_ids = move_lines.ids
                if not line.concept:
                    line.concept = (_('Move lines: %s') %
                                    ', '.join(move_lines.mapped('name')))
