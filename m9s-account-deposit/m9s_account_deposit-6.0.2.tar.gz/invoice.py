# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal

from trytond.exceptions import UserError, UserWarning
from trytond.i18n import gettext
from trytond.model import ModelView, Workflow, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.wizard import Button, StateTransition, StateView, Wizard

from .exceptions import DepositError


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    deposit = fields.Function(fields.Numeric('Available Deposit',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits', 'party']),
        'on_change_with_deposit')
    use_deposit = fields.Boolean('Recall Deposit',
        states={
            'invisible': Eval('state') != 'draft',
            }, depends=['state'])

    @classmethod
    def default_use_deposit(cls):
        return True

    @fields.depends('party')
    def on_change_with_deposit(self, name=None):
        if self.party:
            return self.party.deposit
        else:
            return None

    @classmethod
    @ModelView.button
    @Workflow.transition('posted')
    def post(cls, invoices):
        # Run validate_invoice before posting to set the invoice to a
        # different state than draft to not touch any more the deposit lines.
        cls.validate_invoice(invoices)
        super(Invoice, cls).post(invoices)
        # TODO: check batch posting!! #4504
        # cls.check_deposit(invoices)

    # TODO: check batch posting!! #4504
    @classmethod
    def _post(cls, invoices):
        super()._post(invoices)
        cls.check_deposit(invoices)

    @classmethod
    def write(cls, *args):
        super(Invoice, cls).write(*args)
        cls.manage_deposit(sum(args[::2], []))

    @classmethod
    def manage_deposit(cls, invoices, account=None, description=''):
        pool = Pool()
        Configuration = pool.get('account.configuration')

        if account is None:
            config = Configuration(1)
            account = config.default_account_deposit
            if not account:
                raise DepositError(gettext(
                        'account_deposit.msg_missing_deposit_account'))

        for invoice in invoices:
            if invoice.state == 'draft':
                if invoice.use_deposit and not invoice.sold_deposit():
                    if not description:
                        description = gettext(
                            'account_deposit.msg_deposit_settlement')
                    invoice.call_deposit(account, description)

    def delete_deposit_lines(self, account):
        pool = Pool()
        InvoiceLine = pool.get('account.invoice.line')

        to_delete = []
        for line in self.lines:
            if line.account == account:
                to_delete.append(line)
        if to_delete:
            InvoiceLine.delete(to_delete)

    def call_deposit(self, account, description, maximum=None):
        pool = Pool()
        Currency = pool.get('currency.currency')

        balance = self.party.get_deposit_balance(account)
        balance = Currency.compute(
            account.company.currency, balance, self.currency)
        if maximum is None:
            maximum = self.total_amount
        total_amount = min(maximum, self.total_amount, key=abs)

        self.delete_deposit_lines(account)

        amount = Decimal(0)
        if self.type.startswith('in'):
            if balance > 0 and total_amount > 0:
                amount = -min(balance, total_amount)
        else:
            if balance < 0 and total_amount > 0:
                amount = -min(-balance, total_amount)
        if amount < 0:
            line = self._get_deposit_recall_invoice_line(
                amount, account, description)
            try:
                line.sequence = max(l.sequence for l in self.lines
                    if l.sequence is not None)
            except ValueError:
                pass
            line.save()
        return amount

    def _get_deposit_recall_invoice_line(self, amount, account, description):
        pool = Pool()
        Line = pool.get('account.invoice.line')

        line = Line(
            invoice=self,
            company=self.company,
            type='line',
            quantity=1,
            account=account,
            unit_price=amount,
            description=description,
            )
        # Set taxes
        line.on_change_account()
        return line

    def sold_deposit(self):
        '''
        Check if an outgoing invoice contains lines with positive deposit
        (i.e. invoiced to the customer).
        Obviously this could also refer to credit notes, but they don't need
        to be handled, too.
        '''
        if self.type == 'out':
            if any([l for l in self.lines
                        if l.type == 'line'
                        and l.account.type.deposit
                        and l.amount > Decimal('0')]):
                    return True
        return False

    @classmethod
    def check_deposit(cls, invoices):
        pool = Pool()
        Configuration = pool.get('account.configuration')
        config = Configuration(1)

        to_check = set()
        for invoice in invoices:
            if not invoice.use_deposit or invoice.sold_deposit():
                continue
            deposit_used = Decimal(0)
            for line in invoice.lines:
                if line.type != 'line':
                    continue
                if line.account.type.deposit:
                    deposit_used += line.amount
            if deposit_used != Decimal(0):
                sign = 1 if invoice.type.startswith('in') else -1
                to_check.add((invoice.party, line.account, sign,
                        deposit_used))

        for party, account, sign, deposit_used in to_check:
            if config.deposit_settlement_method == 'strict':
                if not party.check_deposit(account, sign):
                    raise DepositError(gettext(
                            'account_deposit.deposit_not_enough',
                            account=account.rec_name,
                            party=party.rec_name))
            elif config.deposit_settlement_method == 'partial':
                if not party.check_deposit(account, sign,
                        deposit_used=deposit_used):
                    warning_name = 'deposit_changed_%s' % party.code
                    raise UserWarning(warning_name, gettext(
                                'account_deposit.msg_deposit_changed',
                                party=party.rec_name))


class InvoiceLine(metaclass=PoolMeta):
    __name__ = 'account.invoice.line'

    @classmethod
    def _account_domain(cls, type_):
        domain = super(InvoiceLine, cls)._account_domain(type_)
        return domain + [('type.deposit', '=', True)]


class DepositRecall(Wizard):
    'Recall deposit on Invoice'
    __name__ = 'account.invoice.recall_deposit'
    start = StateView('account.invoice.recall_deposit.start',
        'account_deposit.recall_deposit_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Recall', 'recall', 'tryton-ok', default=True),
            ])
    recall = StateTransition()

    def default_start(self, fields):
        pool = Pool()
        Configuration = pool.get('account.configuration')

        config = Configuration(1)
        account = config.default_account_deposit
        description = gettext('account_deposit.msg_deposit_settlement')

        return {
            'company': self.record.company.id,
            'account': account.id,
            'description': description,
            }

    def transition_recall(self):
        self.record.call_deposit(self.start.account, self.start.description)
        return 'end'


class DepositRecallStart(ModelView):
    'Recall deposit on Invoice'
    __name__ = 'account.invoice.recall_deposit.start'
    company = fields.Many2One('company.company', 'Company', readonly=True)
    account = fields.Many2One('account.account', 'Account', required=True,
        domain=[
            ('type.deposit', '=', True),
            ('company', '=', Eval('company', -1)),
            ],
        depends=['company'])
    description = fields.Text('Description', required=True)
