from odoo.tests.common import SavepointCase
import unittest
from mock import Mock, patch


class TestAccountPaymentLineCreateWizard(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountPaymentLineCreateWizard, cls).setUpClass()
        cls.company = cls.env.user.company_id
        cls.invoice_line_account = cls.env['account.account'].search(
            [('user_type_id', '=', cls.env.ref(
                'account.data_account_type_expenses').id)],
            limit=1).id
        if not cls.invoice_line_account:
            raise unittest.SkipTest('No account found')
        cls.invoice = cls._create_supplier_invoice()
        cls.mode = cls.env.ref(
            'account_payment_mode.payment_mode_outbound_ct1')
        cls.mode.default_journal_ids = cls.env['account.journal'].search([
            ('type', 'in', ('purchase', 'purchase_refund')),
            ('company_id', '=', cls.env.user.company_id.id)
        ])
        cls.creation_mode = cls.env.ref(
            'account_payment_mode.payment_mode_outbound_dd1')
        cls.creation_mode.default_journal_ids = (
            cls.env['account.journal'].search([
                ('type', 'in', ('sale', 'sale_refund')),
                ('company_id', '=', cls.env.user.company_id.id)
            ]))
        cls.bank_journal = cls.env['account.journal'].search(
            [('type', '=', 'bank'),
             '|', ('company_id', '=', cls.env.user.company_id.id),
             ('company_id', '=', False)], limit=1)
        # Make sure no other payment orders are in the DB
        cls.domain = [
            ('state', '=', 'draft'),
            ('payment_type', '=', 'outbound'),
        ]
        cls.env['account.payment.order'].search(cls.domain).unlink()
        cls.mode.group_lines = True
        cls.creation_mode.write({
            'group_lines': False,
            'bank_account_link': 'fixed',
            'default_date_prefered': 'due',
            'fixed_journal_id': cls.bank_journal.id,
        })
        cls.mode.variable_journal_ids = cls.bank_journal
        cls.invoice.action_invoice_open()
        order_vals = {
            'payment_type': 'outbound',
            'payment_mode_id': cls.creation_mode.id,
        }
        cls.order = cls.env['account.payment.order'].create(order_vals)

        cls.order.payment_mode_id = cls.mode.id
        cls.order.payment_mode_id_change()

    @classmethod
    def _create_supplier_invoice(cls):
        invoice_account = cls.env['account.account'].search(
            [('user_type_id', '=', cls.env.ref(
                'account.data_account_type_payable').id)],
            limit=1).id
        invoice = cls.env['account.invoice'].create({
            'partner_id': cls.env.ref('base.res_partner_4').id,
            'account_id': invoice_account,
            'type': 'in_invoice',
            'payment_mode_id': cls.env.ref(
                'account_payment_mode.payment_mode_outbound_ct1').id
        })

        for i in range(1, 62):
            cls.env['account.invoice.line'].create({
                'product_id': cls.env.ref('product.product_product_4').id,
                'quantity': 1.0,
                'price_unit': i * 100.0,
                'invoice_id': invoice.id,
                'name': 'product that cost '+str(i*100),
                'account_id': cls.invoice_line_account,
            })

        return invoice

    @patch(
        'odoo.addons.account_payment_order.wizard.account_payment_line_create.AccountPaymentLineCreate._prepare_move_line_domain', # noqa
    )
    def test_grouped_create_payment_lines(self, MockPrepareMoveLineDomain):
        line_create = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=self.order.id
        ).create({})
        line_create.payment_mode = 'any'
        line_create.limit = 5
        line_create.queue_enabled = False
        line_create.move_line_filters_change()
        line_ids = [line.id for line in self.invoice.move_id.line_ids if line.debit > 0]
        MockPrepareMoveLineDomain.return_value = [('id', 'in', line_ids)]
        line_create.populate()
        line_create.create_payment_lines()
        orders_after = self.env['account.payment.order'].search([])
        self.assertEquals(13, len(orders_after))

    @patch(
        'odoo.addons.account_payment_order.wizard.account_payment_line_create.AccountPaymentLineCreate._prepare_move_line_domain', # noqa
    )
    def test_grouped_create_payment_lines_exact_groups(self, MockPrepareMoveLineDomain):
        line_create = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=self.order.id
        ).create({})
        line_create.payment_mode = 'any'
        line_create.limit = 5
        line_create.queue_enabled = False
        line_create.move_line_filters_change()
        line_ids = [line.id for line in self.invoice.move_id.line_ids if line.debit > 0]
        line_ids = line_ids[:-1]
        MockPrepareMoveLineDomain.return_value = [('id', 'in', line_ids)]
        line_create.populate()
        line_create.create_payment_lines()
        orders_after = self.env['account.payment.order'].search([])
        self.assertEquals(12, len(orders_after))

    @patch(
        'odoo.addons.account_payment_order.wizard.account_payment_line_create.AccountPaymentLineCreate._prepare_move_line_domain', # noqa
    )
    def test_grouped_create_payment_lines_queued(self, MockPrepareMoveLineDomain):
        line_create = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=self.order.id
        ).create({})
        line_create.payment_mode = 'any'
        line_create.limit = 5
        line_create.move_line_filters_change()
        line_ids = [line.id for line in self.invoice.move_id.line_ids if line.debit > 0]
        MockPrepareMoveLineDomain.return_value = [('id', 'in', line_ids)]
        line_create._prepare_move_line_domain = Mock(
            return_value=[('id', 'in', line_ids)]
        )
        line_create.populate()
        queue_jobs_before = self.env['queue.job'].search_count([])
        line_create.create_payment_lines()
        queue_jobs_after = self.env['queue.job'].search_count([])
        self.assertEquals(13, queue_jobs_after - queue_jobs_before)

    @patch(
        'odoo.addons.account_payment_order.wizard.account_payment_line_create.AccountPaymentLineCreate._prepare_move_line_domain', # noqa
    )
    def test_create_payment_lines(self, MockPrepareMoveLineDomain):
        line_create = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=self.order.id
        ).create({})
        line_create.payment_mode = 'any'
        line_create.limit_enabled = False
        line_create.queue_enabled = False
        line_create.move_line_filters_change()
        line_ids = [line.id for line in self.invoice.move_id.line_ids if line.debit > 0]
        MockPrepareMoveLineDomain.return_value = [('id', 'in', line_ids)]
        line_create._prepare_move_line_domain = Mock(
            return_value=[('id', 'in', line_ids)]
        )
        line_create.populate()
        orders_before = self.env['account.payment.order'].search([])
        payment_lines_before = self.env['account.payment.line'].search([])
        line_create.create_payment_lines()
        orders_after = self.env['account.payment.order'].search([])
        payment_lines_after = self.env['account.payment.line'].search([])
        self.assertEquals(0, len(orders_after) - len(orders_before))
        self.assertEquals(61, len(payment_lines_after) - len(payment_lines_before))

    def test_prepare_move_line_domain_due_date(self):
        line_create = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=self.order.id
        ).create({})
        line_create.date_type = "due"
        line_create.due_date = "2021-01-15"
        line_create.due_date_from = "2021-01-01"
        domain = line_create._prepare_move_line_domain()
        self.assertIn(('date_maturity', '<=', line_create.due_date), domain)
        self.assertNotEqual(
            '|',
            domain[domain.index(('date_maturity', '<=', line_create.due_date))-1],
        )
        self.assertIn(('date_maturity', '>=', line_create.due_date_from), domain)

    def test_prepare_move_line_domain_move_date(self):
        line_create = self.env['account.payment.line.create'].with_context(
            active_model='account.payment.order',
            active_id=self.order.id
        ).create({})
        line_create.date_type = "move"
        line_create.move_date = "2021-01-15"
        line_create.move_date_from = "2021-01-01"
        domain = line_create._prepare_move_line_domain()
        self.assertIn(('date', '<=', line_create.move_date), domain)
        self.assertIn(('date', '>=', line_create.move_date_from), domain)
