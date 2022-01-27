# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import carrier, stock

__all__ = ['register']


def register():
    Pool.register(
        carrier.Carrier,
        stock.ShipmentOut,
        stock.ShipmentInReturn,
        module='stock_package_rate_ups', type_='model')
    Pool.register(
        stock.GetRate,
        stock.GetRateUPS,
        stock.CreateShippingUPS,
        module='stock_package_rate_ups', type_='wizard')
