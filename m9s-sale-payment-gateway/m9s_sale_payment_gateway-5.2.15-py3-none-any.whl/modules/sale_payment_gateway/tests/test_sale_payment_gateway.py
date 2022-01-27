# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest

from decimal import Decimal

from trytond.exceptions import UserError
from trytond.modules.company.tests import set_company
from trytond.modules.currency.tests import add_currency_rate, create_currency
from trytond.modules.invoice_payment_gateway.tests import create_payment_term
from trytond.modules.payment_gateway.tests import (
    create_payment_gateway, create_payment_profile)
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite
from trytond.tests.test_tryton import with_transaction
from trytond.transaction import Transaction


def create_sale(payment_authorize_on='manual',
        payment_capture_on='manual', amount=Decimal('200')):
    """
    Create test sale with provided amount, payment_authorized and payment
    capture options.
    """
    pool = Pool()
    Currency = pool.get('currency.currency')
    Party = pool.get('party.party')
    Company = pool.get('company.company')
    Sale = pool.get('sale.sale')
    Account = pool.get('account.account')
    Journal = pool.get('account.journal')

    payment_term = create_payment_term()

    currencies = Currency.search([
            ('code', '=', 'USD'),
            ])
    if currencies:
        currency = currencies[0]
    else:
        currency = create_currency('USD')
        try:
            add_currency_rate(currency, Decimal('1'))
        except:
            pass

    company, = Company.search([])
    with set_company(company):
        journal_revenue, = Journal.search([
                ('code', '=', 'REV'),
                ])
        journal_expense, = Journal.search([
                ('code', '=', 'EXP'),
                ])
        journal_cash, = Journal.search([
                ('code', '=', 'CASH'),
                ])
        revenue, = Account.search([
                ('type.revenue', '=', True),
                ])
        receivable, = Account.search([
                ('type.receivable', '=', True),
                ])

        with Transaction().set_context(company=company.id):
            party, = Party.create([{
                        'name': 'Bruce Wayne',
                        'addresses': [('create', [{
                                        'name': 'Bruce Wayne',
                                        'city': 'Gotham',
                                        }])],
                        'customer_payment_term': payment_term,
                        'account_receivable': receivable,
                        'contact_mechanisms': [('create', [
                                    {'type': 'mobile', 'value': '8888888888'},
                                    ])],
                        }])

            sale, = Sale.create([{
                        'reference': 'Test Sale',
                        'payment_term': payment_term,
                        'currency': currency,
                        'party': party.id,
                        'invoice_address': party.addresses[0].id,
                        'shipment_address': party.addresses[0].id,
                        'company': company.id,
                        'invoice_method': 'manual',
                        'shipment_method': 'manual',
                        'payment_authorize_on': payment_authorize_on,
                        'payment_capture_on': payment_capture_on,
                        'lines': [('create', [{
                                        'description': 'Some item',
                                        'unit_price': amount,
                                        'quantity': 1,
                                        }])]
                        }])
    return sale


def confirm_sale_by_completing_payments(sales):
    """
    Confirm sale and complete payments.
    """
    pool = Pool()
    Sale = pool.get('sale.sale')

    Sale.confirm(sales)
    for sale in sales:
        sale.process_pending_payments()


def process_sale_by_completing_payments(sales):
    """
    Process sale and complete payments.
    """
    pool = Pool()
    Sale = pool.get('sale.sale')

    Sale.process(sales)
    for sale in sales:
        sale.process_pending_payments()


# Set True for dev to enable only single tests by commenting the decorator
skip = False


class SalePaymentGatewayTestCase(ModuleTestCase):
    'Test Sale Payment Gateway module'
    module = 'sale_payment_gateway'

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0005_single_payment_CASE1(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'manual'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='manual', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        payment_details = {
            'sale': sale.id,
            'amount': Decimal('200'),
            'gateway': gateway,
            'payment_profile': profile,
            }
        with Transaction().set_context(company=company.id):
            payment_details.update({
                    'credit_account': SalePayment(
                        **payment_details).on_change_with_credit_account()
                    })
            payment = SalePayment(**payment_details)
            payment.save()

        self.assertTrue(payment.description.startswith("Paid by Card"))
        self.assertTrue(payment.credit_account)
        self.assertEqual(payment.credit_account, sale.party.account_receivable)
        self.assertEqual(payment.company.id, sale.company.id)

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            # confirm and process the sale, payment will not go
            # through because capture and auth is manual.
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0010_single_payment_CASE2(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'sale_confirm'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='sale_confirm', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0012_single_payment_CASE2B(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'sale_confirm'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        Draft > Quote > Confirm
        ===================================
        Total Sale Amount       |   $200
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        Cancel > Draft (line x 2 )> Quote > Confirm
        ===================================
        Total Sale Amount       |   $400
        Total Payment Lines     |     2
        Payment 1               |   $400
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='sale_confirm', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # ===================================
        # Draft > Quote > Confirm
        # ===================================
        Sale.draft([sale])
        self.assertEqual(sale.state, 'draft')

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # ===========================================
        # Cancel > Draft (line x 2 )> Quote > Confirm
        # ===========================================
        # Standard behaviour of Tryton is to not allow cancelling from
        # confirmed state, but only from draft and quotation.
        # Nevertheless downstream modules can do all kind of shit
        # by allowing cancelling of orders also from confirmed state.
        # Deal with it too, because in the real world, people fucking cancel!
        Sale.cancel([sale])
        # sale should still be in confirmed state
        Sale.draft([sale])
        # sale must now be in draft state
        self.assertEqual(sale.state, 'draft')

        sale = Sale(sale.id)
        self.assertEqual(sale.state, 'draft')
        SaleLine.write([sale.lines[0]], {'quantity': 2})

        sale = Sale(sale.id)
        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id,
                language='en'):
            Sale.quote([sale])
            with self.assertRaises(UserError):
                # Complain, because there is not enough money!
                confirm_sale_by_completing_payments([sale])

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0013_single_payment_CASE2C(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'sale_confirm'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        Cancel > Draft (line x 2 )> Quote > Confirm
        ===================================
        Total Sale Amount       |   $400
        Total Payment Lines     |     2
        Payment 1               |   $200
        Payment 2               |   $200
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')
        SalePayment = pool.get('sale.payment')
        Party = pool.get('party.party')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='sale_confirm', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            # Re-browse the party with the new context
            party = Party(sale.party.id)
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': party.account_receivable,
                }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # ===================================
        # Draft > Quote > Confirm
        # ===================================
        Sale.draft([sale])
        self.assertEqual(sale.state, 'draft')

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # ===========================================
        # Cancel > Draft (line x 2 )> Quote > Confirm
        # ===========================================
        # Standard behaviour of Tryton is to not allow cancelling from
        # confirmed state, but only from draft and quotation.
        # Nevertheless downstream modules can do all kind of shit
        # by allowing cancelling of orders also from confirmed state.
        # Deal with it too, because in the real world, people fucking cancel!
        Sale.cancel([sale])
        # sale should still be in confirmed state
        Sale.draft([sale])
        # sale must now be in draft state
        self.assertEqual(sale.state, 'draft')
        SaleLine.write([sale.lines[0]], {'quantity': 2})

        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a second payment
        with Transaction().set_context(company=company.id):
            # Re-browse the party with the new context
            party = Party(sale.party.id)
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': party.account_receivable,
                }])

            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('400'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('400'))
        self.assertEqual(sale.payment_captured, Decimal('400'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0014_single_payment_CASE2D(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'sale_confirm'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        Cancel > Draft (line x 2 )> Quote > Confirm
        ===================================
        Total Sale Amount       |   $400
        Total Payment Lines     |     1 (Expansion of lines)
        Payment 1               |   $200
        Payment 2               |   $200
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')
        SalePayment = pool.get('sale.payment')
        Party = pool.get('party.party')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='sale_confirm', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            # Re-browse the party with the new context
            party = Party(sale.party.id)
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': party.account_receivable,
                }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # ===================================
        # Draft > Quote > Confirm
        # ===================================
        Sale.draft([sale])
        self.assertEqual(sale.state, 'draft')

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # ===========================================
        # Cancel > Draft (line x 2 )> Quote > Confirm
        # ===========================================
        # Standard behaviour of Tryton is to not allow cancelling from
        # confirmed state, but only from draft and quotation.
        # Nevertheless downstream modules can do all kind of shit
        # by allowing cancelling of orders also from confirmed state.
        # Deal with it too, because in the real world, people fucking cancel!
        Sale.cancel([sale])
        # sale should still be in confirmed state
        Sale.draft([sale])
        # sale must now be in draft state
        self.assertEqual(sale.state, 'draft')

        # Expand the sale total amount
        SaleLine.write([sale.lines[0]], {'quantity': 2})

        sale = Sale(sale.id)
        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Expand the payment
        SalePayment.write([payment], {'amount': Decimal('400')})

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('400'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('400'))
        self.assertEqual(sale.payment_captured, Decimal('400'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0015_single_payment_CASE3(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='sale_process', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0020_single_payment_CASE4(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'manual'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='manual', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('200'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('200'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0022_single_payment_CASE4A(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'manual'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        Cancel > Draft (line x 2 )> Quote > Confirm
        ===================================
        Total Sale Amount       |   $400
        Total Payment Lines     |     2
        Payment 1               |   $200 (Problemo)
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='manual', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('200'))

        # ===========================================
        # Cancel > Draft (line x 2 )> Quote > Confirm
        # ===========================================
        # Standard behaviour of Tryton is to not allow cancelling from
        # confirmed state, but only from draft and quotation.
        # Nevertheless downstream modules can do all kind of shit
        # by allowing cancelling of orders also from confirmed state.
        # Deal with it too, because in the real world, people fucking cancel!
        Sale.cancel([sale])
        # sale should still be in confirmed state
        Sale.draft([sale])
        # sale must now be in draft state
        self.assertEqual(sale.state, 'draft')

        SaleLine.write([sale.lines[0]], {'quantity': 2})

        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('200'))

        with Transaction().set_context(company=company.id,
                language='en'):
            Sale.quote([sale])

            with self.assertRaises(UserError):
                # Complain, because there is not enough money!
                #process_sale_by_completing_payments([sale])
                confirm_sale_by_completing_payments([sale])

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0022_single_payment_CASE4B(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'manual'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        Cancel > Draft (line x 2 )> Quote > Confirm
        ===================================
        Total Sale Amount       |   $400
        Total Payment Lines     |     2
        Payment 1               |   $400 (No problemo)
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')
        SalePayment = pool.get('sale.payment')
        Party = pool.get('party.party')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='manual', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('200'))

        # ===========================================
        # Cancel > Draft (line x 2 )> Quote > Confirm
        # ===========================================
        # Standard behaviour of Tryton is to not allow cancelling from
        # confirmed state, but only from draft and quotation.
        # Nevertheless downstream modules can do all kind of shit
        # by allowing cancelling of orders also from confirmed state.
        # Deal with it too, because in the real world, people fucking cancel!
        Sale.cancel([sale])
        # sale should still be in confirmed state
        Sale.draft([sale])
        # sale must now be in draft state
        self.assertEqual(sale.state, 'draft')

        SaleLine.write([sale.lines[0]], {'quantity': 2})

        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('200'))

        # Create a second payment
        with Transaction().set_context(company=company.id):
            # Re-browse the party with the new context
            party = Party(sale.party.id)
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': party.account_receivable,
                }])
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('400'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('400'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('400'))

        # Now process the sale, the values should remain identical, since we
        # have choosen method manual
        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.total_amount, Decimal('400'))
        self.assertEqual(sale.payment_total, Decimal('400'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('400'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('400'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0025_single_payment_CASE5(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'sale_confirm'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='sale_confirm', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        # No authorized amount because it was captured after that.
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0030_single_payment_CASE6(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='sale_process', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('200'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0035_single_payment_CASE7(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_process'
        Payment Capture On:     | 'manual'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_process',
            payment_capture_on='manual', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('200'))


    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0040_single_payment_CASE8(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_process'
        Payment Capture On:     | 'sale_confirm'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        SaleConfiguration = pool.get('sale.configuration')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_process'
        sale_config.payment_capture_on = 'sale_confirm'

        # This is an invalid setting so it should raise an user error.
        with self.assertRaises(UserError):
            sale_config.save()

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0045_single_payment_CASE9(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_process'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $200
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_process',
            payment_capture_on='sale_process', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway)
        with Transaction().set_context(company=company.id):
            payment, = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('200'),
                'gateway': gateway,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        # Authorize amount is zero because payment captured after that
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0050_multi_payment_CASE1(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'manual'
        ===================================
        Total Payment Lines     |     2
        Payment 1   (manual)    |   $100
        Payment 2   (cc)        |   $100
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway_cash = create_payment_gateway()
        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='manual', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway_dummy)
        with Transaction().set_context(company=company.id, language='en'):
            payment_cash, payment_dummy = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_cash,
                'credit_account': sale.party.account_receivable,
                }, {
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_dummy,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])
            #self.assertEqual(payment_cash.description, 'Paid by Cash')

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            # confirm and process the sale, payment will not go
            # through because capture and auth is manual.
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('100'))
        self.assertEqual(sale.payment_collected, Decimal('100'))
        self.assertEqual(sale.payment_captured, Decimal('100'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))


    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0055_multi_payment_CASE2(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'sale_confirm'
        ===================================
        Total Payment Lines     |     2
        Payment 1 (manual)      |   $100
        Payment 2 (cc)          |   $100
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway_cash = create_payment_gateway()
        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='sale_confirm', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway_dummy)
        with Transaction().set_context(company=company.id, language='en'):
            payment_cash, payment_dummy = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_cash,
                'credit_account': sale.party.account_receivable,
                }, {
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_dummy,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0060_multi_payment_CASE3(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'manual'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     2
        Payment 1 (manual)      |   $100
        Payment 2 (cc)          |   $100
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway_cash = create_payment_gateway()
        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='manual',
            payment_capture_on='sale_process', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway_dummy)
        with Transaction().set_context(company=company.id, language='en'):
            payment_cash, payment_dummy = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_cash,
                'credit_account': sale.party.account_receivable,
                }, {
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_dummy,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0065_multi_payment_CASE4(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'manual'
        ===================================
        Total Payment Lines     |     2
        Payment 1 (manual)      |   $100
        Payment 2 (cc)          |   $100
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway_cash = create_payment_gateway()
        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='manual', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway_dummy)
        with Transaction().set_context(company=company.id, language='en'):
            payment_cash, payment_dummy = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_cash,
                'credit_account': sale.party.account_receivable,
                }, {
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_dummy,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('100'))
        self.assertEqual(sale.payment_collected, Decimal('100'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('100'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('100'))
        self.assertEqual(sale.payment_authorized, Decimal('100'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0070_multi_payment_CASE5(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'sale_confirm'
        ===================================
        Total Payment Lines     |     2
        Payment 1 (manual)      |   $100
        Payment 2 (cc)          |   $100
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway_cash = create_payment_gateway()
        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='sale_confirm', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway_dummy)
        with Transaction().set_context(company=company.id, language='en'):
            payment_cash, payment_dummy = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_cash,
                'credit_account': sale.party.account_receivable,
                }, {
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_dummy,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        # No authorized amount because it was captured after that.
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0075_multi_payment_CASE6(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     2
        Payment 1 (manual)      |   $100
        Payment 2 (cc)          |   $100
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway_cash = create_payment_gateway()
        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='sale_process', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway_dummy)
        with Transaction().set_context(company=company.id, language='en'):
            payment_cash, payment_dummy = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_cash,
                'credit_account': sale.party.account_receivable,
                }, {
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_dummy,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('100'))
        self.assertEqual(sale.payment_collected, Decimal('100'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('100'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0080_multi_payment_CASE7(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_process'
        Payment Capture On:     | 'manual'
        ===================================
        Total Payment Lines     |     2
        Payment 1 (manual)      |   $100
        Payment 2 (cc)          |   $100
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway_cash = create_payment_gateway()
        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_process',
            payment_capture_on='manual', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway_dummy)
        with Transaction().set_context(company=company.id, language='en'):
            payment_cash, payment_dummy = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_cash,
                'credit_account': sale.party.account_receivable,
                }, {
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_dummy,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('100'))
        self.assertEqual(sale.payment_authorized, Decimal('100'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0085_multi_payment_CASE8(self):
        """
        ===================================
        Total Sale Amount       |   $200
        Payment Authorize On:   | 'sale_process'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     2
        Payment 1 (manual)      |   $100
        Payment 2 (cc)          |   $100
        ===================================
        """
        pool = Pool()
        Sale = pool.get('sale.sale')
        SalePayment = pool.get('sale.payment')

        gateway_cash = create_payment_gateway()
        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_process',
            payment_capture_on='sale_process', amount=Decimal('200'))

        self.assertEqual(sale.total_amount, Decimal('200'))
        self.assertEqual(sale.payment_total, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        # Create a payment
        company = sale.company
        profile = create_payment_profile(sale.party, gateway_dummy)
        with Transaction().set_context(company=company.id, language='en'):
            payment_cash, payment_dummy = SalePayment.create([{
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_cash,
                'credit_account': sale.party.account_receivable,
                }, {
                'sale': sale,
                'amount': Decimal('100'),
                'gateway': gateway_dummy,
                'payment_profile': profile,
                'credit_account': sale.party.account_receivable,
            }])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            Sale.quote([sale])
            confirm_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('200'))
        self.assertEqual(sale.payment_collected, Decimal('0'))
        self.assertEqual(sale.payment_captured, Decimal('0'))
        self.assertEqual(sale.payment_authorized, Decimal('0'))

        with Transaction().set_context(company=company.id):
            process_sale_by_completing_payments([sale])

        self.assertEqual(sale.payment_total, Decimal('200'))
        self.assertEqual(sale.payment_available, Decimal('0'))
        self.assertEqual(sale.payment_collected, Decimal('200'))
        self.assertEqual(sale.payment_captured, Decimal('200'))
        # Authorize amount is zero because payment captured after
        # that.
        self.assertEqual(sale.payment_authorized, Decimal('0'))

    @unittest.skipIf(skip is True, "skip for now")
    @with_transaction()
    def test_0090_test_duplicate_sale(self):
        """
        Test if payment_processing_state is not copied in duplicate sales
        """
        pool = Pool()
        Sale = pool.get('sale.sale')

        gateway_dummy = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_confirm',
            payment_capture_on='sale_process', amount=Decimal('200'))

        sale.payment_processing_state = 'waiting_for_capture'
        sale.save()

        self.assertEqual(
            sale.payment_processing_state, 'waiting_for_capture')

        new_sales = Sale.copy([sale])
        self.assertTrue(new_sales)
        self.assertEqual(len(new_sales), 1)
        self.assertIsNone(new_sales[0].payment_processing_state)
        self.assertFalse(new_sales[0].payments)

    @unittest.skip
    @with_transaction()
    def test_0100_test_sale_payment_wizard(self):
        """
        Test the wizard used to create sale payments

        Note: This test is skipped for now
        Usage of payment profiles was disabled for missing GDPR compliance
        in commit 254454ec0e1d0064ed075a055910ec3c63f237c6
        """
        pool = Pool()
        SalePayment = pool.get('sale.payment')
        SalePaymentWizard = pool.get('sale.payment.add', type="wizard")
        PaymentProfile = pool.get('party.payment_profile')

        cash_gateway = create_payment_gateway()
        dummy_gateway = create_payment_gateway(method='dummy')
        sale = create_sale(payment_authorize_on='sale_process',
            payment_capture_on='sale_process', amount=Decimal('200'))

        company = sale.company
        # Case I: Manual Payment
        sale_payment_wizard1 = SalePaymentWizard(
            SalePaymentWizard.create()[0]
        )

        # Test default_payment_info
        with Transaction().set_context(company=company.id, active_id=sale.id):
            defaults = sale_payment_wizard1.default_payment_info()
            self.assertEqual(defaults['sale'], sale.id)
            self.assertEqual(defaults['party'], sale.party.id)
            self.assertEqual(
                defaults['currency_digits'], sale.currency_digits
            )

        sale_payment_wizard1.payment_info.sale = sale.id
        sale_payment_wizard1.payment_info.credit_account = \
            sale.party.account_receivable.id
        sale_payment_wizard1.payment_info.party = sale.party.id
        sale_payment_wizard1.payment_info.gateway = cash_gateway.id
        sale_payment_wizard1.payment_info.method = cash_gateway.method
        sale_payment_wizard1.payment_info.amount = 100
        sale_payment_wizard1.payment_info.payment_profile = None
        sale_payment_wizard1.payment_info.currency_digits = \
            sale_payment_wizard1.payment_info.get_currency_digits(
                name='currency_digits'
            )
        sale_payment_wizard1.payment_info.reference = 'Reference-1'
        sale_payment_wizard1.payment_info.gift_card = None

        with Transaction().set_context(active_id=sale.id):
            sale_payment_wizard1.transition_add()

        payment1, = SalePayment.search([
            ('sale', '=', sale.id),
            ('company', '=', company.id),
        ], limit=1)
        self.assertEqual(payment1.amount, 100)
        self.assertEqual(payment1.party, sale.party)
        self.assertEqual(payment1.method, cash_gateway.method)
        self.assertEqual(payment1.provider, cash_gateway.provider)
        self.assertEqual(payment1.reference, 'Reference-1')

        # Case II: Credit Card Payment with new payment profile
        sale_payment_wizard2 = SalePaymentWizard(
            SalePaymentWizard.create()[0]
        )

        # Test if party has 1 payment profile already created
        payment_profiles = PaymentProfile.search([
            ('party', '=', sale.party.id)
        ])
        self.assertEqual(len(payment_profiles), 1)

        sale_payment_wizard2.payment_info.sale = sale.id
        sale_payment_wizard2.payment_info.credit_account = \
            sale.party.account_receivable.id
        sale_payment_wizard2.payment_info.party = sale.party.id
        sale_payment_wizard2.payment_info.gateway = dummy_gateway.id
        sale_payment_wizard2.payment_info.method = \
            sale_payment_wizard2.payment_info.get_method()
        sale_payment_wizard2.payment_info.use_existing_card = False
        sale_payment_wizard2.payment_info.amount = 55
        sale_payment_wizard2.payment_info.owner = sale.party.name
        sale_payment_wizard2.payment_info.number = '4111111111111111'
        sale_payment_wizard2.payment_info.expiry_month = '01'
        sale_payment_wizard2.payment_info.expiry_year = '2018'
        sale_payment_wizard2.payment_info.csc = '911'
        sale_payment_wizard2.payment_info.payment_profile = None
        sale_payment_wizard2.payment_info.reference = 'Reference-2'
        sale_payment_wizard2.payment_info.gift_card = None

        with Transaction().set_context(active_id=sale.id):
            sale_payment_wizard2.transition_add()

        payment2, = SalePayment.search([
            ('sale', '=', sale.id),
            ('amount', '=', 55),
            ('company', '=', company.id),
        ], limit=1)
        self.assertEqual(payment2.method, dummy_gateway.method)
        self.assertEqual(payment2.provider, dummy_gateway.provider)

        # Test if new payment profile was created for party
        new_payment_profile = PaymentProfile.search([
            ('party', '=', sale.party.id)
        ], order=[('id', 'DESC')])
        self.assertEqual(len(new_payment_profile), 2)
        self.assertEqual(
            new_payment_profile[0], payment2.payment_profile
        )

        # Case III: Credit Card Payment with existing card
        sale_payment_wizard3 = SalePaymentWizard(
            SalePaymentWizard.create()[0]
        )

        sale_payment_wizard3.payment_info.sale = sale.id
        sale_payment_wizard3.payment_info.credit_account = \
            sale.party.account_receivable.id
        sale_payment_wizard3.payment_info.party = sale.party.id
        sale_payment_wizard3.payment_info.gateway = dummy_gateway.id
        sale_payment_wizard3.payment_info.method = dummy_gateway.method
        sale_payment_wizard3.payment_info.use_existing_card = True
        sale_payment_wizard3.payment_info.amount = 45
        sale_payment_wizard3.payment_info.payment_profile = \
            new_payment_profile[0]
        sale_payment_wizard3.payment_info.reference = 'Reference-3'
        sale_payment_wizard3.payment_info.gift_card = None

        with Transaction().set_context(active_id=sale.id):
            sale_payment_wizard3.transition_add()

        payment3, = SalePayment.search([
            ('sale', '=', sale.id),
            ('amount', '=', 45),
            ('company', '=', company.id),
        ], limit=1)
        self.assertEqual(payment3.method, dummy_gateway.method)
        self.assertEqual(payment3.provider, dummy_gateway.provider)
        self.assertEqual(
            new_payment_profile[0], payment3.payment_profile
        )

        self.assertEqual(SalePayment.search([], count=True), 3)
        # Delete a payment
        SalePayment.delete([payment3])
        self.assertEqual(SalePayment.search([], count=True), 2)


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            SalePaymentGatewayTestCase))
    return suite
