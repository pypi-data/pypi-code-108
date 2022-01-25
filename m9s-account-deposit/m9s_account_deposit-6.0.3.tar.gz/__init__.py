# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import account, configuration, contract, invoice, party


def register():
    Pool.register(
        account.AccountTypeTemplate,
        account.AccountType,
        configuration.Configuration,
        configuration.ConfigurationDefaultAccount,
        configuration.ConfigurationDepositSettlementMethod,
        invoice.Invoice,
        invoice.InvoiceLine,
        invoice.DepositRecallStart,
        party.Party,
        module='account_deposit', type_='model')
    Pool.register(
        contract.ContractConsumption,
        module='account_deposit', type_='model', depends=['contract'])
    Pool.register(
        account.Reconcile,
        invoice.DepositRecall,
        party.Erase,
        module='account_deposit', type_='wizard')
