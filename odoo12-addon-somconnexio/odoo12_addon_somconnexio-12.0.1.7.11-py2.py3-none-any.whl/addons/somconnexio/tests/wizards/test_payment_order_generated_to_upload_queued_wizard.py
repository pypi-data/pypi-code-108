from ..sc_test_case import SCTestCase


class TestPaymentOrderGeneratedToUploadQueuedWizard(SCTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPaymentOrderGeneratedToUploadQueuedWizard, cls).setUpClass()
        cls.env = cls.env(context=dict(
            cls.env.context,
            test_queue_job_no_delay=False,  # jobs reactivated
        ))

        cls.wizard_obj = cls.env['payment.order.generated.uploaded.queued']
        cls.queue_obj = cls.env['queue.job']
        cls.inbound_mode = cls.env.ref(
            'account_payment_mode.payment_mode_inbound_dd1'
        )
        cls.invoice_line_account = cls.env['account.account'].search(
            [('user_type_id', '=', cls.env.ref(
                'account.data_account_type_revenue').id)],
            limit=1).id
        cls.journal = cls.env['account.journal'].search(
            [('type', '=', 'bank'),
             '|', ('company_id', '=', cls.env.user.company_id.id),
             ('company_id', '=', False)], limit=1
        )
        cls.inbound_mode.variable_journal_ids = cls.journal
        # Make sure no others orders are present
        cls.domain = [
            ('state', '=', 'draft'),
            ('payment_type', '=', 'inbound'),
        ]
        cls.payment_order_obj = cls.env['account.payment.order']
        cls.payment_order_obj.search(cls.domain).unlink()
        # Create payment order
        cls.inbound_order = cls.env['account.payment.order'].create({
            'payment_type': 'inbound',
            'payment_mode_id': cls.inbound_mode.id,
            'journal_id': cls.journal.id,
        })
        # Open invoice
        cls.invoice = cls._create_customer_invoice()
        cls.invoice.action_invoice_open()
        # Add to payment order using the wizard
        cls.env['account.invoice.payment.line.multi'].with_context(
            active_model='account.invoice',
            active_ids=cls.invoice.ids
        ).create({}).run()

    @classmethod
    def _create_customer_invoice(cls):
        invoice_account = cls.env['account.account'].search(
            [('user_type_id', '=', cls.env.ref(
                'account.data_account_type_receivable').id)],
            limit=1).id
        invoice = cls.env['account.invoice'].create({
            'partner_id': cls.env.ref('base.res_partner_4').id,
            'account_id': invoice_account,
            'type': 'out_invoice',
            'payment_mode_id': cls.inbound_mode.id
        })
        cls.env['account.invoice.line'].create({
            'product_id': cls.env.ref('product.product_product_4').id,
            'quantity': 1.0,
            'price_unit': 100.0,
            'invoice_id': invoice.id,
            'name': 'product that cost 100',
            'account_id': cls.invoice_line_account,
        })
        return invoice

    def test_mark_to_upload(self):
        payment_order = self.inbound_order
        # Set journal to allow cancelling entries
        self.journal.update_posted = True
        payment_order.write({
            'journal_id': self.journal.id,
        })
        # Open payment order
        payment_order.draft2open()
        # Generate and upload
        payment_order.open2generated()
        payment_order.generated2uploaded_job()
        self.assertEqual(payment_order.state, 'uploaded')

    def test_queue_mark_to_upload(self):
        payment_order = self.inbound_order
        wizard = self.wizard_obj.with_context(
            active_ids=payment_order.ids,
        ).create({})
        self.journal.update_posted = True
        payment_order.write({
            'journal_id': self.journal.id,
        })
        # Open payment order
        payment_order.draft2open()
        # Generate and upload
        payment_order.open2generated()
        prev_jobs = self.queue_obj.search([])
        wizard.run()
        current_jobs = self.queue_obj.search([])
        jobs = current_jobs - prev_jobs
        self.assertEqual(len(jobs), 1)
        self.assertTrue(self.inbound_order.set_uploaded_job_ids)
