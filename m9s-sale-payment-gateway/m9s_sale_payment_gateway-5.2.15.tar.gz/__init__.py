# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool

from . import configuration, ir, payment, sale

__all__ = ['register']


def register():
    Pool.register(
        configuration.SaleConfiguration,
        ir.Cron,
        payment.Payment,
        sale.Sale,
        sale.PaymentTransaction,
        sale.AskSalePaymentView,
        sale.AddSalePaymentView,
        module='sale_payment_gateway', type_='model')
    Pool.register(
        sale.AddSalePayment,
        module='sale_payment_gateway', type_='wizard')
