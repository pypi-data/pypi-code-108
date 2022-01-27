# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal

from trytond.exceptions import UserError
from trytond.i18n import gettext
from trytond.model import ModelView, Workflow, fields
from trytond.modules.payment_gateway.transaction import BaseCreditCardViewMixin
from trytond.pool import Pool, PoolMeta
from trytond.pyson import And, Bool, Eval, If, Not, Or
from trytond.transaction import Transaction
from trytond.wizard import Button, StateTransition, StateView, Wizard

READONLY_STATES = {
    'readonly': Eval('state').in_(['cancel', 'processing', 'done'])
}
DEPENDS = ['state']


class Sale(metaclass=PoolMeta):
    'Sale'
    __name__ = 'sale.sale'

    # Readonly because the wizard should be the one adding payment gateways as
    # it provides a more cusomizable UX than directly adding a record.
    # For example, taking CC numbers.
    payments = fields.One2Many(
        'sale.payment', 'sale', 'Payments', states={
            'readonly': Eval('state').in_(['done', 'cancel'])
        },
    )
    sorted_payments = fields.Function(
        fields.One2Many('sale.payment', None, 'Payments'),
        'get_sorted_payments'
    )

    # Sale must be able to define when it should authorize and capture the
    # payments.
    payment_authorize_on = fields.Selection(
        'get_authorize_options', 'Authorize payments', required=True,
        states=READONLY_STATES, depends=DEPENDS
    )
    payment_capture_on = fields.Selection(
        'get_capture_options', 'Capture payments', required=True,
        states=READONLY_STATES, depends=DEPENDS
    )

    gateway_transactions = fields.Function(
        fields.One2Many(
            'payment_gateway.transaction', None, 'Gateway Transactions',
        ), "get_gateway_transactions"
    )
    payment_total = fields.Function(
        fields.Numeric(
            'Total Payment', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'],
            help="Total value of payments"
        ), 'get_payment',
    )
    payment_collected = fields.Function(
        fields.Numeric(
            'Payment Collected', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'],
            help="Total value of payments collected"
        ), 'get_payment',
    )
    payment_refunded = fields.Function(
        fields.Numeric(
            'Payment Refunded', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'],
            help="Total value of payments refunded"
        ), 'get_payment',
    )
    payment_available = fields.Function(
        fields.Numeric(
            'Payment Remaining', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'],
            help="Total value which is neither authorize nor captured"
        ), 'get_payment',
    )
    payment_authorized = fields.Function(
        fields.Numeric(
            'Payment Authorized', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'],
            help="Amount authorized to be catured"
        ), 'get_payment',
    )
    payment_captured = fields.Function(
        fields.Numeric(
            'Payment Captured', digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits'],
            help="Amount already captured"
        ), 'get_payment',
    )
    payment_processing_state = fields.Selection([
        (None, 'None'),
        ('waiting_for_auth', 'Waiting For Authorization'),
        ('waiting_for_capture', 'Waiting For Capture'),
    ], "Payment Processing State", select=True, readonly=True)

    @staticmethod
    def default_payment_processing_state():
        return None

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        cls._buttons.update({
            'add_payment': {
                'invisible': Eval('state').in_(['cancel', 'draft']),
            },
            'auth_capture': {
                'invisible': Eval('state').in_(['cancel', 'draft', 'done']),
            },
        })

    @classmethod
    def validate(cls, sales):
        super(Sale, cls).validate(sales)

        for sale in sales:
            sale.validate_payment_combination()

    def validate_payment_combination(self):
        if self.payment_authorize_on == 'sale_process' and \
                self.payment_capture_on == 'sale_confirm':
            raise UserError(gettext('sale_payment_gateway.auth_before_capture'))

    @classmethod
    def get_authorize_options(cls):
        """Return all the options from sale configuration.
        """
        SaleConfiguration = Pool().get('sale.configuration')
        field_name = 'payment_authorize_on'
        selection = SaleConfiguration.fields_get(
            [field_name])[field_name]['selection']
        return selection

    @classmethod
    def get_capture_options(cls):
        """Return all the options from sale configuration.
        """
        SaleConfiguration = Pool().get('sale.configuration')
        field_name = 'payment_capture_on'
        selection = SaleConfiguration.fields_get(
            [field_name])[field_name]['selection']
        return selection

    @staticmethod
    def default_payment_authorize_on():
        SaleConfiguration = Pool().get('sale.configuration')

        return SaleConfiguration(1).payment_authorize_on

    @staticmethod
    def default_payment_capture_on():
        SaleConfiguration = Pool().get('sale.configuration')

        return SaleConfiguration(1).payment_capture_on

    @classmethod
    def get_payment_method_priority(cls):
        """
        Priority order for payment methods. Downstream modules can override
        this method to change the method priority.
        """
        return ('manual', 'credit_card', 'dummy')

    def get_gateway_transactions(self, name):
        GatewayTransaction = Pool().get('payment_gateway.transaction')

        return list(map(
            int, GatewayTransaction.search(
                [('sale_payment', 'in', list(map(int, self.payments)))]
            )
        ))

    def get_payment(self, name):
        """Return amount from payments.
        """
        Payment = Pool().get('sale.payment')

        payments = Payment.search([('sale', '=', self.id)])

        if name == 'payment_total':
            return Decimal(sum([payment.amount for payment in payments]))

        elif name == 'payment_available':
            return Decimal(
                sum([payment.amount_available for payment in payments])
            )

        elif name == 'payment_captured':
            return Decimal(sum(
                [payment.amount_captured for payment in payments]
            ))

        elif name == 'payment_authorized':
            return Decimal(sum(
                [payment.amount_authorized for payment in payments]
            ))

        elif name == 'payment_refunded':
            return Decimal(sum(
                [payment.amount_refunded for payment in payments]
            ))

        elif name == 'payment_collected':
            return self.payment_total - self.payment_available

    @classmethod
    @ModelView.button_action('sale_payment_gateway.wizard_add_payment')
    def add_payment(cls, sales):
        pass

    def get_sorted_payments(self, name=None):
        """
        Return the payments in the order they should be consumed
        """
        payment_method_priority = self.get_payment_method_priority()
        return list(map(int, sorted(
            self.payments,
            key=lambda t: payment_method_priority.index(t.method)
        )))

    def _raise_sale_payments_waiting(self):
        if self.payment_processing_state == 'waiting_for_auth':
            raise UserError(
                gettext('sale_payment_gateway.payments_waiting_authorization'))
        elif self.payment_processing_state == 'waiting_for_capture':
            raise UserError(
                gettext('sale_payment_gateway.payments_waiting_capture'))

    def check_total_payment(self, amount, threshold=0):
        """
        Check the amount to pay against the total amount of payments.
        """
        amount_to_pay = amount - self.payment_total
        if amount_to_pay > threshold:
            raise UserError(
                gettext('sale_payment_gateway.insufficient_amount',
                    amount_missing=amount_to_pay,
                    amount_available=self.payment_available,
                    amount_collected=self.payment_collected,
                    number_payments=len(self.payments)))

    def authorize_payments(self, amount, description='', threshold=0):
        """
        Authorize sale payments. It actually creates payment transactions
        corresponding to sale payments and set the payment processing state to
        `waiting to auth`.
        """
        if not description:
            description = gettext('sale_payment_gateway.payment_from_sale')
        if self.payment_processing_state:
            self._raise_sale_payments_waiting()

        if (amount - self.payment_available) > threshold:
            raise UserError(
                gettext('sale_payment_gateway.insufficient_amount',
                    amount_missing=amount,
                    amount_available=self.payment_available,
                    amount_collected=self.payment_collected,
                    number_payments=len(self.payments)))

        transactions = []
        for payment in self.sorted_payments:
            if not amount:
                break

            if not payment.amount_available or payment.method == "manual":
                # * if no amount available, continue to next.
                # * manual payment need not to be authorized.
                continue

            # The amount to authorize is the amount_available if the
            # amount_available is less than the amount we seek.
            authorize_amount = min(amount, payment.amount_available)

            payment_transaction = payment._create_payment_transaction(
                authorize_amount, description
            )
            payment_transaction.save()

            amount -= authorize_amount

            transactions.append(payment_transaction)

        self.payment_processing_state = "waiting_for_auth"
        self.save()

        return transactions

    def capture_payments(self, amount, description='', threshold=0):
        """Capture sale payments.

        * If existing authorizations exist, capture them
        * If not, capture available payments directly
        """
        if not description:
            description = gettext('sale_payment_gateway.payment_from_sale')
        if self.payment_processing_state:
            self._raise_sale_payments_waiting()

        # Raise a user error if
        # - the amount is greater than the completed + posted payments (without
        #   authorized)
        #   (payment_available is the difference between amounts of the
        #   payments and authorized + completed + posted transactions)
        if ((amount - self.payment_available - self.payment_authorized)
                > threshold):
            raise UserError(
                gettext('sale_payment_gateway.insufficient_amount',
                    amount_missing=amount,
                    amount_available=self.payment_available,
                    amount_collected=self.payment_collected,
                    number_payments=len(self.payments)))

        transactions = []
        authorized_transactions = [transaction for transaction
            in self.gateway_transactions if transaction.state == 'authorized']
        for transaction in authorized_transactions:
            if not amount:
                break       # pragma: no cover

            capture_amount = min(amount, transaction.amount)

            # Write the new amount of the transaction as the amount
            # required to be captured
            transaction.amount = capture_amount
            transaction.save()

            amount -= capture_amount

            transactions.append(transaction)

        for payment in self.sorted_payments:
            if not amount:
                break

            if not payment.amount_available:
                continue

            # The amount to capture is the amount_available if the
            # amount_available is less than the amount we seek.
            authorize_amount = min(amount, payment.amount_available)

            payment_transaction = payment._create_payment_transaction(
                authorize_amount, description
            )
            payment_transaction.save()

            amount -= authorize_amount

            transactions.append(payment_transaction)

        self.payment_processing_state = "waiting_for_capture"
        self.save()

        return transactions

    @classmethod
    def auth_capture(cls, sales):
        """
        A button triggered version of authorizing or capturing payment directly
        from an order.
        """
        for sale in sales:
            if sale.state == 'confirmed':
                sale.handle_payment_on_confirm()
            elif sale.state == 'processing':
                sale.handle_payment_on_process()
            sale.process_pending_payments()

    def handle_pos_payments(self, mode='capture'):
        '''
        Add compatibility with the sale_payment_channel module
        '''
        pos_paid_amount = Decimal('0.0')
        if hasattr(self, 'paid_amount'):
            pos_paid_amount = self.paid_amount
        amount_to_pay = (
            self.total_amount - pos_paid_amount - self.payment_captured)
        if mode == 'authorize':
            amount_to_pay -= self.payment_authorized
        if amount_to_pay <= Decimal('0.0'):
            self.payment_processing_state = None
            self.save()
        return amount_to_pay

    def handle_payment_on_confirm(self):
        if self.payment_capture_on == 'sale_confirm':
            amount_to_pay = self.handle_pos_payments(mode='capture')
            if amount_to_pay > Decimal('0.0'):
                self.capture_payments(amount_to_pay)
        elif self.payment_authorize_on == 'sale_confirm':
            amount_to_pay = self.handle_pos_payments(mode='authorize')
            if amount_to_pay > Decimal('0.0'):
                self.authorize_payments(amount_to_pay)

    def handle_payment_on_process(self):
        if self.payment_capture_on == 'sale_process':
            amount_to_pay = self.handle_pos_payments(mode='capture')
            if amount_to_pay > Decimal('0.0'):
                self.capture_payments(amount_to_pay)
        elif self.payment_authorize_on == 'sale_process':
            amount_to_pay = self.handle_pos_payments(mode='authorize')
            if amount_to_pay > Decimal('0.0'):
                self.authorize_payments(amount_to_pay)

    def settle_manual_payments(self):
        """
        Manual payments should be settled when the order is processed. This is
        separated into a different method so downstream modules can change this
        behavior to adapt to different workflows
        """
        for payment in self.payments:
            if payment.amount_available and payment.method == "manual" and \
                    not payment.payment_transactions:
                payment_transaction = payment._create_payment_transaction(
                    payment.amount_available,
                    gettext('sale_payment_gateway.post_manual_payments'))
                payment_transaction.save()
                payment.capture()
                # m9s self.payment_processing_state = None

    @classmethod
    @ModelView.button
    @Workflow.transition('confirmed')
    def confirm(cls, sales):
        super(Sale, cls).confirm(sales)

        for sale in [s for s in sales if s.invoice_state != 'paid']:
            sale.handle_payment_on_confirm()

    @classmethod
    def process(cls, sales):
        for sale in [s for s in sales if (s.state == 'confirmed' and
                    s.invoice_state != 'paid')]:
            # Sequence of the next statements is important
            sale.settle_manual_payments()
            sale.handle_payment_on_process()
            #sale.settle_manual_payments()
        super(Sale, cls).process(sales)

    def _get_amount_to_checkout(self):
        """
        Returns the amount which needs to be paid

        Downstream modules can override this method to change it as
        per their requirement
        """
        return self.total_amount - self.payment_total

    def _pay_using_credit_card(self, gateway, credit_card, amount):
        '''
        Complete using the given credit card and finish the transaction.
        :param gateway: Active record of the payment gateway to process card
        :param credit_card: A dictionary with either of the following
                            information sets:
                            * owner: name of the owner (unicode)
                            * number: number of the credit card
                            * expiry_month: expiry month (int or string)
                            * expiry_year: year as string
                            * cvv: the cvv number
                            In future this method will accept track1 and track2
                            as valid information.
        :param amount: Decimal amount to charge the card for
        '''
        TransactionUseCardWizard = Pool().get(
            'payment_gateway.transaction.use_card', type='wizard'
        )
        PaymentTransaction = Pool().get('payment_gateway.transaction')

        # Manual card based operation
        payment_transaction = PaymentTransaction(
            party=self.party,
            address=self.invoice_address,
            amount=amount,
            currency=self.currency,
            gateway=gateway,
            sale=self,
        )
        payment_transaction.save()

        use_card_wiz = TransactionUseCardWizard(
            TransactionUseCardWizard.create()[0]        # Wizard session
        )
        use_card_wiz.card_info.owner = credit_card['owner']
        use_card_wiz.card_info.number = credit_card['number']
        use_card_wiz.card_info.expiry_month = credit_card['expiry_month']
        use_card_wiz.card_info.expiry_year = credit_card['expiry_year']
        use_card_wiz.card_info.csc = credit_card['cvv']

        with Transaction().set_context(active_id=payment_transaction.id):
            use_card_wiz.transition_capture()

    def _pay_using_profile(self, payment_profile, amount):
        '''
        Complete the Checkout using a payment_profile. Only available to the
        registered users of the website.
        :param payment_profile: Active record of payment profile
        :param amount: Decimal amount to charge the card for
        '''
        PaymentTransaction = Pool().get('payment_gateway.transaction')

        if payment_profile.party != self.party:
            raise UserError(gettext('sale_payment_gateway.different_profile_owner',
                    payment_profile.party.name,
                    self.party.name))

        payment_transaction = PaymentTransaction(
            party=self.party,
            address=self.invoice_address,
            payment_profile=payment_profile,
            amount=amount,
            currency=self.currency,
            gateway=payment_profile.gateway,
            sale=self,
        )
        payment_transaction.save()

        PaymentTransaction.capture([payment_transaction])

    def handle_payment_transactions_failure(self, transactions, **kwargs):
        pass

    def process_pending_payments(self, **kwargs):
        """Process waiting payments for corresponding sale.
        """
        PaymentTransaction = Pool().get('payment_gateway.transaction')

        # Transactions waiting for auth or capture.
        txns = PaymentTransaction.search([
            ('sale_payment.sale', '=', self.id),
            ('state', '!=', 'failed')
        ])
        if self.payment_processing_state == "waiting_for_auth":
            for payment in self.sorted_payments:
                payment.authorize()
            self.payment_processing_state = None

        elif self.payment_processing_state == "waiting_for_capture":

            # Settle authorized transactions
            PaymentTransaction.settle(
                [txn for txn in txns if txn.state == 'authorized'])

            # Capture other transactions
            PaymentTransaction.capture(
                [txn for txn in txns if txn.state == "draft"])

            self.payment_processing_state = None
        else:
            # Trigger the check for the total payment amount.
            # This is to provide a safety net when changing a sale after
            # cancelation or re-drafting and there is no
            # payment_processing_state set.
            self.check_total_payment(self.total_amount)
            return
        self.save()

        self.handle_payment_transactions_failure(txns, **kwargs)

    @classmethod
    def process_all_pending_payments(cls):
        """Cron method authorizes waiting payments.
        """
        User = Pool().get('res.user')

        user = User(Transaction().user)
        if not (Transaction().context.get('company') or user.company):
            # Processing payments without user's company and company in
            # context is not possible at all. Skip the execution.
            return

        sales = cls.search([
            ('payment_processing_state', '!=', None)
        ])

        for sale in sales:
            sale.process_pending_payments()

    @classmethod
    def copy(cls, records, default=None):
        """
        Duplicating records
        """
        if default is None:
            default = {}

        default['payment_processing_state'] = None
        default['payments'] = []

        return super(Sale, cls).copy(records, default)


class PaymentTransaction(metaclass=PoolMeta):
    "Gateway Transaction"
    __name__ = 'payment_gateway.transaction'

    sale_payment = fields.Many2One(
        'sale.payment', 'Sale Payment', ondelete='RESTRICT', select=True,
        states={
            'readonly': Eval('state') != 'draft'
            }, depends=['state'])

    def get_shipping_address(self, name):
        return self.sale_payment and self.sale_payment.sale and \
            self.sale_payment.sale.shipment_address.id

    @classmethod
    def _get_origin(cls):
        'Add sale to the selections'
        res = super(PaymentTransaction, cls)._get_origin()
        res.append('sale.sale')
        return res


class AskSalePaymentView(ModelView):
    'View for asking before proceeding'
    __name__ = 'sale.payment.ask_view'
    message = fields.Text('Message', readonly=True)


class AddSalePaymentView(BaseCreditCardViewMixin, ModelView):
    """
    View for adding Sale Payments
    """
    __name__ = 'sale.payment.add_view'

    sale = fields.Many2One(
        'sale.sale', 'Sale', required=True, readonly=True
    )

    party = fields.Many2One('party.party', 'Party', readonly=True)
    gateway = fields.Many2One(
        'payment_gateway.gateway', 'Gateway', required=True,
        domain=[('users', '=', Eval('user'))],
        depends=['user']
    )
    currency_digits = fields.Function(
        fields.Integer('Currency Digits'),
        'get_currency_digits'
    )
    method = fields.Function(
        fields.Char('Payment Gateway Method'), 'get_method'
    )
    use_existing_card = fields.Boolean(
        'Use existing Card?', states={
            'invisible': Eval('method') != 'credit_card'
        }, depends=['method']
    )
    payment_profile = fields.Many2One(
        'party.payment_profile', 'Payment Profile',
        domain=[
            ('party', '=', Eval('party')),
            ('gateway', '=', Eval('gateway')),
        ],
        states={
            #'required': And(
            #    Eval('method') == 'credit_card',
            #    Bool(Eval('use_existing_card'))
            #    ),
            'invisible': Or(
                ~Eval('use_existing_card'),
                ~Eval('gateway'),
                Eval('method') == 'manual',
                ),
        }, depends=['method', 'use_existing_card', 'party', 'gateway']
    )
    amount = fields.Numeric(
        'Amount', digits=(16, Eval('currency_digits', 2)),
        required=True, depends=['currency_digits'],
    )
    reference = fields.Char(
        'Reference', states={
            'invisible': Not(Eval('method') == 'manual'),
        }
    )
    user = fields.Many2One(
        "res.user", "Tryton User", readonly=True
    )

    company = fields.Many2One(
        'company.company', 'Company', readonly=True, required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
        ],
    )
    credit_account = fields.Many2One(
        'account.account', 'Credit Account', required=True
    )

    @classmethod
    def __setup__(cls):
        super(AddSalePaymentView, cls).__setup__()

        INV = Or(
            Eval('method') == 'manual',
            ~Bool(Eval('gateway')),
            And(
                Eval('method') == 'credit_card',
                Bool(Eval('use_existing_card'))
            )
        )
        STATE1 = {
            #'required': And(
            #    ~Bool(Eval('use_existing_card')),
            #    Eval('method') == 'credit_card'
            #),
            'invisible': INV
        }
        DEPENDS = ['use_existing_card', 'method']

        cls.owner.states.update(STATE1)
        cls.owner.depends.extend(DEPENDS)
        cls.number.states.update(STATE1)
        cls.number.depends.extend(DEPENDS)
        cls.expiry_month.states.update(STATE1)
        cls.expiry_month.depends.extend(DEPENDS)
        cls.expiry_year.states.update(STATE1)
        cls.expiry_year.depends.extend(DEPENDS)
        cls.csc.states.update(STATE1)
        cls.csc.depends.extend(DEPENDS)
        cls.swipe_data.states = {'invisible': INV}
        cls.swipe_data.depends = ['method']

        cls.credit_account.domain = [
            ('company', '=', Eval('company', -1)),
            ('type.receivable', '=', True),
        ]
        cls.credit_account.depends = ['company']

    def get_currency_digits(self, name):
        return self.sale.currency_digits if self.sale else 2

    def get_method(self, name=None):
        """
        Return the method based on the gateway
        """
        return self.gateway.method

    @staticmethod
    def default_use_existing_card():
        return False

    #@fields.depends('party')
    #def on_change_party(self):
    #    if self.party and self.party.payment_profiles:
    #        if len(self.party.payment_profiles) == 1:
    #            self.payment_profile = self.party.payment_profiles[0]
    #        self.use_existing_card = True
    #    else:
    #        self.payment_profile = None
    #        self.use_existing_card = False

    @fields.depends('gateway')
    def on_change_gateway(self):
        if self.gateway:
            self.method = self.gateway.method or None


class AddSalePayment(Wizard):
    """
    Wizard to add a Sale Payment
    """
    __name__ = 'sale.payment.add'

    start_state = 'check'
    check = StateTransition()
    ask = StateView('sale.payment.ask_view',
        'sale_payment_gateway.sale_payment_ask_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Proceed', 'payment_info', 'tryton-ok', default=True)
            ])
    payment_info = StateView(
        'sale.payment.add_view',
        'sale_payment_gateway.sale_payment_add_view_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add', 'add', 'tryton-ok', default=True)
        ]
    )
    add = StateTransition()
    finish = StateTransition()

    def default_ask(self, data):
        return {
            'message': self.ask.message,
            }

    def default_payment_info(self, fields=None):
        Sale = Pool().get('sale.sale')

        sale = Sale(Transaction().context.get('active_id'))

        res = {
            'sale': sale.id,
            'company': sale.company.id,
            'party': sale.party.id,
            'credit_account': sale.party.account_receivable.id,
            'owner': sale.party.name,
            'currency_digits': sale.currency_digits,
            'amount': sale._get_amount_to_checkout(),
            'user': Transaction().user,
        }
        return res

    def transition_check(self):
        """
        Check step to show evtl. problems before proceeding
        """
        Sale = Pool().get('sale.sale')

        # Check for evtl. missing shipment costs
        sale = Sale(Transaction().context.get('active_id'))
        if (hasattr(Sale, 'carrier')
                and sale.state == 'draft'
                and sale.carrier):
            if not [l for l in sale.lines if l.shipment_cost]:
                msg = gettext(
                    'sale_payment_gateway.msg_ask_shipment_cost',
                    sale=sale.rec_name)
                self.ask.message = msg
                return 'ask'
        return 'payment_info'

    def create_sale_payment(self, profile=None):
        """
        Helper function to create a new payment
        or return an existing payment for the gateway.
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        sale = Sale(Transaction().context.get('active_id'))
        payments = [p for p in sale.payments
            if p.gateway == self.payment_info.gateway]
        if payments:
            return payments[0]
        payment_profile = profile
        if self.payment_info.method != 'credit_card':
            payment_profile = None

        payment = SalePayment(
            sale=sale.id,
            credit_account=self.payment_info.credit_account,
            party=self.payment_info.party,
            gateway=self.payment_info.gateway,
            payment_profile=payment_profile,
            amount=self.payment_info.amount,
            reference=self.payment_info.reference or None,
        )
        return payment

    def create_payment_profile(self):
        """
        Helper function to create payment profile
        """
        Sale = Pool().get('sale.sale')
        ProfileWizard = Pool().get(
            'party.party.payment_profile.add', type="wizard"
        )
        profile_wizard = ProfileWizard(
            ProfileWizard.create()[0]
        )
        profile_wizard.card_info.owner = self.payment_info.owner
        profile_wizard.card_info.number = self.payment_info.number
        profile_wizard.card_info.expiry_month = self.payment_info.expiry_month
        profile_wizard.card_info.expiry_year = self.payment_info.expiry_year
        profile_wizard.card_info.csc = self.payment_info.csc or ''
        profile_wizard.card_info.gateway = self.payment_info.gateway
        profile_wizard.card_info.provider = self.payment_info.gateway.provider
        profile_wizard.card_info.party = self.payment_info.party

        billing_address = Sale(
            Transaction().context.get('active_id')
        ).invoice_address
        if not billing_address:
            # If no billing address fallback to party's invoice address
            try:
                billing_address = self.payment_info.party.address_get(
                    type='invoice'
                )
            except AttributeError:
                # account_invoice module is not installed
                pass

        profile_wizard.card_info.address = billing_address

        with Transaction().set_context(return_profile=True):
            profile = profile_wizard.transition_add()
        return profile

    def transition_add(self):
        """
        Creates a new payment
        """
        profile = self.payment_info.payment_profile
        payment = self.create_sale_payment(profile=profile)
        payment.save()
        return 'finish'

    def transition_finish(self):
        """
        Ends the wizard

        Override to append further processing (e.g. card data)
        """
        return 'end'
