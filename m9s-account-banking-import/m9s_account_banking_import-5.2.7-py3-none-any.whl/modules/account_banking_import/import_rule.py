# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import re

from decimal import Decimal

from simpleeval import simple_eval

from trytond.model import ModelSQL, ModelView, fields, sequence_ordered
from trytond.pool import Pool
from trytond.pyson import Eval, If
from trytond.tools import decistmt
from trytond.transaction import Transaction


class BankingImportRule(sequence_ordered(), ModelSQL, ModelView):
    "Banking Import Rule"
    __name__ = 'banking.import.rule'

    name = fields.Char("Name")

    company = fields.Many2One('company.company', "Company")
    bank_import_config = fields.Many2One('banking.import.configuration',
        "Bank Import Configuration",
        domain=[
            If(Eval('company'),
                ('company', '=', Eval('company')),
                ()),
            ],
        depends=['company'])
    amount_low = fields.Numeric(
        "Amount Low",
        digits=(16, Eval('currency_digits', 2)),
        domain=[If(Eval('amount_high'),
                ['OR',
                    ('amount_low', '=', None),
                    ('amount_low', '<=', Eval('amount_high')),
                    ],
                [])],
        depends=['currency_digits', 'amount_high'])
    amount_high = fields.Numeric(
        "Amount High",
        digits=(16, Eval('currency_digits', 2)),
        domain=[If(Eval('amount_low'),
                ['OR',
                    ('amount_high', '=', None),
                    ('amount_high', '>=', Eval('amount_low')),
                    ],
                [])],
        depends=['currency_digits', 'amount_low'])
    information_rules = fields.One2Many(
        'banking.import.rule.information', 'rule', "Information Rules")

    lines = fields.One2Many(
        'banking.import.rule.line', 'rule', "Lines")

    currency_digits = fields.Function(
        fields.Integer("Currency Digits"),
        'on_change_with_currency_digits')

    @fields.depends('bank_import_config')
    def on_change_with_currency_digits(self, name=None):
        if self.bank_import_config:
            return self.bank_import_config.journal.currency.digits
        return None

    def match(self, origin):
        keywords = {}
        if self.company and self.company != origin.bank_import_config.company:
            return False
        if self.bank_import_config and self.bank_import_config != origin.bank_import_config:
            return False
        if self.amount_low is not None and self.amount_low > origin.amount:
            return False
        if self.amount_high is not None and self.amount_high < origin.amount:
            return False
        if self.information_rules:
            for irule in self.information_rules:
                result = irule.match(origin)
                if isinstance(result, dict):
                    keywords.update(result)
                elif not result:
                    return False
        keywords.update(amount=origin.amount, pending=origin.amount)
        return keywords

    def apply(self, origin, keywords):
        keywords = keywords.copy()
        for rule_line in self.lines:
            line = rule_line.get_line(origin, keywords)
            if not line:
                return
            keywords['pending'] -= line.amount
            yield line


class BankingImportRuleInformation(sequence_ordered(), ModelSQL, ModelView):
    "Banking Import Rule Information"
    __name__ = 'banking.import.rule.information'

    rule = fields.Many2One(
        'banking.import.rule', "Rule", required=True, ondelete='CASCADE')
    key = fields.Selection('get_key_selection', "Key", required=True)
    key_value = fields.Function(
        fields.Char("Match Value"), 'on_change_with_key_value')
    boolean = fields.Boolean("Boolean",
        states={
            'invisible': Eval('key_type') != 'boolean',
            },
        depends=['key_type'])
    char = fields.Char("Char",
        states={
            'invisible': Eval('key_type') != 'char',
            },
        depends=['key_type'],
        help="The regular expression the key information is searched with.\n"
        "It may define the groups named:\n"
        "party, bank_account, invoice.")
    text = fields.Text("Text",
        states={
            'invisible': Eval('key_type') != 'text',
            },
        depends=['key_type'],
        help="The regular expression the key information is searched with.\n"
        "It may define the groups named:\n"
        "party, bank_account, invoice.")
    selection = fields.Selection(
        'get_selections', "Selection",
        states={
            'invisible': Eval('key_type') != 'selection',
            },
        depends=['key_type'])
    key_type = fields.Function(
        fields.Selection('get_key_types', "Key Type"),
        'on_change_with_key_type')

    # 6.0
    #@classmethod
    #def __setup__(cls):
    #    super().__setup__()
    #    cls.__access__.add('rule')

    @classmethod
    def key_selection_excludes(cls):
        return ['amount', 'balance', 'bank_import_config', 'batch_lines',
            'create_uid', 'create_date', 'date', 'id', 'rec_name',
            'valuta_date', 'write_uid', 'write_date']

    @classmethod
    def get_key_selection(cls):
        pool = Pool()
        ImportLine = pool.get('banking.import.line')

        excludes = cls.key_selection_excludes()
        selection = []
        for _field in ImportLine.fields_get().items():
            if _field[0] in excludes:
                continue
            selection.append((_field[0], _field[1]['string']))
        return selection

    @classmethod
    def get_key_types(cls):
        types = set([v['type'] for v in cls.fields_get().values()])
        return [(x, y) for x, y in zip(types, types)]

    @fields.depends('key')
    def on_change_with_key_type(self, name=None):
        pool = Pool()
        ImportLine = pool.get('banking.import.line')

        if self.key:
            return ImportLine.fields_get([self.key])[self.key]['type']

    @fields.depends('key', 'key_type')
    def on_change_with_key_value(self, name=None):
        if self.key and self.key_type:
            return getattr(self, self.key_type, '')

    @fields.depends('key')
    def get_selections(self):
        pool = Pool()
        ImportLine = pool.get('banking.import.line')

        key = self.key
        if key and ImportLine.fields_get([key])[key]['type'] == 'selection':
            return ImportLine.fields_get([key])[key]['selection']
        return [(None, '')]

    @classmethod
    def view_attributes(cls):
        return super().view_attributes() + [
            ('//group[@id="%s"]' % type_, 'states', {
                    'invisible': Eval('key_type') != type_,
                    }) for type_ in ['integer', 'float', 'number']]

    def match(self, origin):
        information = getattr(origin, self.key, None)
        if information is None:
            return False
        return getattr(self, '_match_%s' % self.key_type)(
            origin, information)

    def _match_boolean(self, origin, information):
        return self.boolean == information

    def _match_range(self, origin, information):
        low = getattr(self, '%s_low' % self.key_type)
        high = getattr(self, '%s_high' % self.key_type)
        amount = information
        if amount is None:
            return False
        if low is not None and low > amount:
            return False
        if high is not None and high < amount:
            return False
    _match_integer = _match_range
    _match_float = _match_range
    _match_number = _match_range

    def _match_char(self, origin, information):
        result = re.search(
            self.char, information)
        if not result:
            return False
        return result.groupdict()

    def _match_text(self, origin, information):
        result = re.search(
            self.text, information)
        if not result:
            return False
        return result.groupdict()

    def _match_selection(self, origin, information):
        return self.selection == information


def _add_range(cls, name, type_, string):
    low_name = '%s_low' % name
    high_name = '%s_high' % name
    setattr(cls, low_name,
        type_("%s Low" % string,
            domain=[If(Eval(high_name),
                    ['OR',
                        (low_name, '=', None),
                        (low_name, '<=', Eval(high_name)),
                        ],
                    [])],
            states={
                'invisible': Eval('key_type') != name,
                },
            depends=['key_type', high_name]))
    setattr(cls, high_name,
        type_("%s High" % string,
            domain=[If(Eval(low_name),
                    ['OR',
                        (high_name, '=', None),
                        (high_name, '<=', Eval(low_name)),
                        ],
                    [])],
            states={
                'invisible': Eval('key_type') != name,
                },
            depends=['key_type', low_name]))


_add_range(BankingImportRuleInformation, 'integer', fields.Integer, "Integer")
_add_range(BankingImportRuleInformation, 'float', fields.Float, "Float")
_add_range(BankingImportRuleInformation, 'number', fields.Numeric, "Numeric")


class BankingImportRuleLine(sequence_ordered(), ModelSQL, ModelView):
    "Banking Import Rule Line"
    __name__ = 'banking.import.rule.line'

    rule = fields.Many2One(
        'banking.import.rule', "Rule", required=True, ondelete='CASCADE')
    amount = fields.Char(
        "Amount", required=True,
        help="A Python expression evaluated with 'amount' and 'pending'.")
    party = fields.Many2One(
        'party.party', "Party",
        context={
            'company': Eval('company', -1),
            },
        depends=['company'],
        help="Leave empty to use the group named 'party' "
        "from the regular expressions.")
    account = fields.Many2One(
        'account.account', "Account",
        domain=[
            ('company', '=', Eval('company')),
            ('type', '!=', None),
            ('closed', '!=', True),
            ],
        states={
            'readonly': ~Eval('company'),
            },
        depends=['company'],
        help="Leave empty to use the party's receivable or payable account.\n"
        "The rule must have a company to use this field.")
    tax = fields.Many2One('account.tax', 'Tax',
        domain=[
            ('parent', '=', None),
            ('company', '=', Eval('company')),
            ['OR',
                ('start_date', '<=', Eval('date')),
                ('start_date', '=', None),
                ],
            ['OR',
                ('end_date', '>=', Eval('date')),
                ('end_date', '=', None),
                ],
            ],
        states={
            'readonly': ~Eval('company'),
            },
        depends=['company', 'date'],
        help="Leave empty to use the default taxes defined on the account.\n"
        "The rule must have a company to use this field.")
    override_default_tax = fields.Boolean('Override Default Taxes',
        states={
            'readonly': ~Eval('company'),
            },
        depends=['company'],
        help="When activated the tax will override the default taxes "
        "defined on the account.")
    company = fields.Function(
        fields.Many2One('company.company', "Company"),
        'on_change_with_company')
    date = fields.Function(fields.Date('Date'), 'on_change_with_date')
    # 6.0
    #@classmethod
    #def __setup__(cls):
    #    super().__setup__()
    #    cls.__access__.add('rule')

    @staticmethod
    def default_amount():
        return 'pending'

    @fields.depends('rule', '_parent_rule.company')
    def on_change_with_company(self, name=None):
        if self.rule and self.rule.company:
            return self.rule.company.id

    def on_change_with_date(self, name=None):
        pool = Pool()
        Date = pool.get('ir.date')
        return Date.today()

    def get_line(self, origin, keywords, **context):
        pool = Pool()
        BatchLine = pool.get('account.batch.line')
        context.setdefault('functions', {})['Decimal'] = Decimal
        context.setdefault('names', {}).update(keywords)

        journal = origin.bank_import_config.journal
        currency = journal.currency
        amount = currency.round(simple_eval(decistmt(self.amount), **context))
        party = self._get_party(origin, keywords)
        invoice = self._get_invoice(origin, keywords)

        if invoice and party and invoice.party != party:
            return
        if invoice and not party:
            party = invoice.party

        account = self.account
        if not account:
            if invoice:
                account = invoice.account
            elif party:
                with Transaction().set_context(date=origin.date):
                    if amount > Decimal('0.0'):
                        account = party.account_receivable_used
                    else:
                        account = party.account_payable_used

        if not account:
            return
        #if account.party_required and not party:
        #    return

        context = Transaction().context
        line = BatchLine()
        line.batch = context.get('batch')
        line.journal = journal
        line.account = journal.account
        line.bank_imp_line = origin
        line.amount = amount
        line.date = origin._get_entry_date()
        line.party = party
        line.contra_account = account
        if self.override_default_tax:
            line.tax = self.tax
        else:
            line.on_change_contra_account()
        if origin.contra_name:
            line.posting_text = origin.contra_name
        elif origin.purpose.rstrip():
            line.posting_text = origin.purpose.rstrip()
        if invoice:
            line.invoice = invoice
            line.on_change_invoice()
        return line

    def _get_party(self, origin, keywords):
        pool = Pool()
        Party = pool.get('party.party')
        try:
            AccountNumber = pool.get('bank.account.number')
        except KeyError:
            AccountNumber = None

        party = self.party
        if not party:
            if keywords.get('bank_account') and AccountNumber:
                bank_account = keywords['bank_account']
                numbers = AccountNumber.search(['OR',
                        ('number', '=', bank_account),
                        ('number_compact', '=', bank_account),
                        ])
                if len(numbers) == 1:
                    number, = numbers
                    if number.account.owners:
                        party = number.account.owners[0]
            elif keywords.get('party'):
                parties = Party.search(
                    [('rec_name', 'ilike', keywords['party'])])
                if len(parties) == 1:
                    party, = parties
        return party

    def _get_invoice(self, origin, keywords):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        Sale = pool.get('sale.sale')
        if keywords.get('invoice'):
            invoices = Invoice.search([('rec_name', '=', keywords['invoice'])])
            if len(invoices) == 1:
                invoice, = invoices
                return invoice
