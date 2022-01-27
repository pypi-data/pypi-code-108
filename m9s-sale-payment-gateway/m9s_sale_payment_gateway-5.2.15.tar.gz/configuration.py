# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.exceptions import UserError
from trytond.i18n import gettext
from trytond.model import fields
from trytond.pool import PoolMeta


class SaleConfiguration(metaclass=PoolMeta):
    __name__ = 'sale.configuration'

    payment_authorize_on = fields.Selection([
            ('manual', 'Manual'),
            ('sale_confirm', 'Sale Confirm'),
            ('sale_process', 'Sale Process'),
            ], 'Payment Authorize On', required=True,
        )
    payment_capture_on = fields.Selection([
            ('manual', 'Manual'),
            ('sale_confirm', 'Sale Confirm'),
            ('sale_process', 'Sale Process'),
            ], 'Payment Capture On', required=True,
        )

    @classmethod
    def validate(cls, records):
        super(SaleConfiguration, cls).validate(records)

        for record in records:
            record.validate_payment_combination()

    def validate_payment_combination(self):
        if self.payment_authorize_on == 'sale_process' and \
                self.payment_capture_on == 'sale_confirm':
            raise UserError(gettext('sale_payment_gateway.auth_before_capture'))

    @staticmethod
    def default_payment_authorize_on():
        return 'sale_confirm'

    @staticmethod
    def default_payment_capture_on():
        return 'sale_process'
