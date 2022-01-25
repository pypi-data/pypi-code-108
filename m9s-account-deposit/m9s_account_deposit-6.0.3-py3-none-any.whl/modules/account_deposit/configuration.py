# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

_deposit_settlement_methods = [
    ('strict', 'Strict (Require complete deposit per invoice)'),
    ('partial', 'Partial (Allow partial deposit per invoice)'),
    ]


class Configuration(metaclass=PoolMeta):
    __name__ = 'account.configuration'
    default_account_deposit = fields.MultiValue(fields.Many2One(
            'account.account', 'Default Account Deposit',
            domain=[
                ('type.deposit', '=', True),
                ('company', '=', Eval('context', {}).get('company', -1)),
                ]))
    deposit_settlement_method = fields.MultiValue(fields.Selection(
            _deposit_settlement_methods, 'Deposit Settlement Method',
            domain=[
                ('company', '=', Eval('context', {}).get('company', -1)),
                ]))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'default_account_deposit':
            return pool.get('account.configuration.default_account')
        if field == 'default_deposit_settlement_method':
            return pool.get('account.configuration.deposit_settlement_method')
        return super(Configuration, cls).multivalue_model(field)

    @classmethod
    def default_deposit_settlement_method(cls, **pattern):
        return cls.multivalue_model(
            'deposit_settlement_method').default_deposit_settlement_method()


class ConfigurationDefaultAccount(metaclass=PoolMeta):
    __name__ = 'account.configuration.default_account'
    default_account_deposit = fields.Many2One(
        'account.account', 'Default Account Deposit',
        domain=[
            ('type.deposit', '=', True),
            ('company', '=', Eval('company', -1)),
            ],
        depends=['company'])


class ConfigurationDepositSettlementMethod(ModelSQL, CompanyValueMixin):
    'Account Configuration Deposit Settlement Method'
    __name__ = 'account.configuration.deposit_settlement_method'
    configuration = fields.Many2One('account.configuration', 'Configuration',
        required=True, ondelete='CASCADE',
        context={
            'company': Eval('company', -1),
            },
        depends=['company'])
    deposit_settlement_method = fields.Selection(_deposit_settlement_methods,
            'Deposit Settlement Method', required=True)

    @classmethod
    def default_deposit_settlement_method(cls):
        return 'partial'
