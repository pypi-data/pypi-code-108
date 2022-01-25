# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta


class ContractConsumption(metaclass=PoolMeta):
    __name__ = 'contract.consumption'

    @classmethod
    def _invoice(cls, consumptions):
        pool = Pool()
        Invoice = pool.get('account.invoice')

        invoices = super(ContractConsumption, cls)._invoice(consumptions)
        if invoices:
            Invoice.manage_deposit(invoices)
        return invoices
