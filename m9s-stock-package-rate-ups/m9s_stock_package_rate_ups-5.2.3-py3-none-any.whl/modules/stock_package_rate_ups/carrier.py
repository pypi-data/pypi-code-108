# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval


class Carrier(metaclass=PoolMeta):
    __name__ = 'carrier'

    ups_negotiated_rates = fields.Boolean('Use negotiated rates',
        states={
            'invisible': Eval('shipping_service') != 'ups',
            },
        depends=['shipping_service'])
    ups_declare_insurance = fields.Boolean('Declare total value for insurance',
        help = 'Basic insurance amounts to 500 EUR. '
        'For additional insurance the total value must be declared.',
        states={
            'invisible': Eval('shipping_service') != 'ups',
            },
        depends=['shipping_service'])
