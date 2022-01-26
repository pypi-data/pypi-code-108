from ..sc_test_case import SCTestCase
from mock import patch, call, Mock
from odoo.exceptions import UserError


class TestResPartner(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.parent_partner = self.env['res.partner'].create({
            'name': 'test',
            'vat': 'ES00470223B',
            'country_id': self.ref('base.es'),
        })

    def test_contract_email_create(self):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'contract-email'
        })
        self.assertFalse(partner.name)
        self.assertFalse(partner.street)
        self.assertFalse(partner.street2)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
        self.assertFalse(partner.country_id)
        self.assertFalse(partner.customer)
        self.assertFalse(partner.supplier)
        self.assertEqual(partner.email, 'test@example.com')
        self.assertEqual(partner.type, 'contract-email')
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_contract_email_write_set_before(self):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
        })
        partner.write({
            'type': 'contract-email'
        })
        self.assertFalse(partner.name)
        self.assertFalse(partner.street)
        self.assertFalse(partner.street2)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
        self.assertFalse(partner.country_id)
        self.assertFalse(partner.customer)
        self.assertFalse(partner.supplier)
        self.assertEqual(partner.email, 'test@example.com')
        self.assertEqual(partner.type, 'contract-email')
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_contract_email_write_set_in(self):
        partner = self.env['res.partner'].create({})
        partner.write({
            'type': 'contract-email',
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
        })
        self.assertFalse(partner.name)
        self.assertFalse(partner.street)
        self.assertFalse(partner.street2)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
        self.assertFalse(partner.country_id)
        self.assertFalse(partner.customer)
        self.assertFalse(partner.supplier)
        self.assertEqual(partner.email, 'test@example.com')
        self.assertEqual(partner.type, 'contract-email')
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_not_contract_email_create(self):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        self.assertEqual(partner.name, 'test')
        self.assertEqual(partner.street, 'test')
        self.assertEqual(partner.street2, 'test2')
        self.assertEqual(partner.full_street, 'test test2')
        self.assertEqual(partner.city, 'test')
        self.assertEqual(partner.state_id, self.browse_ref('base.state_es_b'))
        self.assertEqual(partner.country_id, self.browse_ref('base.es'))
        self.assertEqual(partner.customer, True)
        self.assertEqual(partner.supplier, False)
        self.assertEqual(partner.email, 'test@example.com')
        self.assertEqual(partner.type, 'representative')
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_error_invoice_partner_create(self):
        vals_partner = {
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'invoice'
        }
        self.assertRaises(
            UserError,
            self.env['res.partner'].create,
            vals_partner
        )

    def test_not_contract_email_write_set_before(self):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
        })
        partner.write({
            'type': 'representative'
        })
        self.assertEqual(partner.name, 'test')
        self.assertEqual(partner.street, 'test')
        self.assertEqual(partner.street2, 'test2')
        self.assertEqual(partner.full_street, 'test test2')
        self.assertEqual(partner.city, 'test')
        self.assertEqual(partner.state_id, self.browse_ref('base.state_es_b'))
        self.assertEqual(partner.country_id, self.browse_ref('base.es'))
        self.assertEqual(partner.customer, True)
        self.assertEqual(partner.supplier, False)
        self.assertEqual(partner.email, 'test@example.com')
        self.assertEqual(partner.type, 'representative')
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_not_contract_email_write_set_in(self):
        partner = self.env['res.partner'].create({})
        partner.write({
            'type': 'representative',
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
        })
        self.assertEqual(partner.name, 'test')
        self.assertEqual(partner.street, 'test')
        self.assertEqual(partner.street2, 'test2')
        self.assertEqual(partner.full_street, 'test test2')
        self.assertEqual(partner.city, 'test')
        self.assertEqual(partner.state_id, self.browse_ref('base.state_es_b'))
        self.assertEqual(partner.country_id, self.browse_ref('base.es'))
        self.assertEqual(partner.customer, True)
        self.assertEqual(partner.supplier, False)
        self.assertEqual(partner.email, 'test@example.com')
        self.assertEqual(partner.type, 'representative')
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_sequence_without_ref_in_creation(self):
        partner_ref = self.browse_ref(
            'somconnexio.sequence_partner'
        ).number_next_actual
        partner = self.env['res.partner'].create({
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        self.assertEquals(str(partner_ref), partner.ref)

    def test_sequence_with_empty_ref_in_manual_UI_creation(self):
        partner_ref = self.browse_ref(
            'somconnexio.sequence_partner'
        ).number_next_actual
        partner = self.env['res.partner'].create({
            'ref': False,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        self.assertEquals(str(partner_ref), partner.ref)

    def test_sequence_with_ref_in_creation(self):
        partner = self.env['res.partner'].create({
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative',
            'ref': '1234'
        })
        self.assertEquals(partner.ref, '1234')

    def test_sequence_in_creation_with_parent_id(self):
        partner = self.env['res.partner'].create({
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative',
            'parent_id': 1
        })
        self.assertEquals(partner.ref, False)

    def test_name_search_customer(self):
        partner = self.env['res.partner'].create({
            'name': 'testName',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative',
            'ref': '1234'
        })
        name_search_results = self.env['res.partner'].name_search(
            args=[['customer', '=', True], ['parent_id', '=', False]],
            limit=8, name='testName', operator='ilike'
        )
        self.assertTrue(name_search_results)
        self.assertEqual(partner.id, name_search_results[0][0])

    def test_name_search_not_customer(self):
        self.env['res.partner'].create({
            'name': 'SEARCH_CUSTOMER',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': False,
            'email': 'test@example.com',
            'type': 'representative',
            'ref': '1234'
        })
        self.assertFalse(self.env['res.partner'].name_search(
            args=[['customer', '=', True], ['parent_id', '=', False]],
            limit=8, name='SEARCH_CUSTOMER', operator='ilike'
        ))

    def test_name_search_contract_email(self):
        self.parent_partner.write({
            'customer': True,
        })
        partner = self.env['res.partner'].create({})
        partner.write({
            'type': 'contract-email',
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'email': 'test@example.com',
        })
        name_search_results = (self.env['res.partner'].name_search(
            args=[['customer', '=', True], ['parent_id', '=', False]],
            limit=8, name='test', operator='ilike'
        ))
        self.assertEquals(len(name_search_results), 1)
        self.assertEquals(name_search_results[0][0], self.parent_partner.id)

    def test_create_normalize_vat(self):
        partner = self.env['res.partner'].create({
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative',
            'ref': '1234',
            'vat': '  44.589.589-H ',
        })

        self.assertEqual(partner.vat, "44589589H")

    def test_write_normalize_vat(self):
        partner = self.env['res.partner'].create({
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative',
            'ref': '1234',
        })
        partner.write({
            'vat': '  44.589.589-H ',
        })

        self.assertEqual(partner.vat, "44589589H")

    def test_has_active_contract(self):
        partner_id = self.parent_partner.id
        mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'icc': '123'
        })
        vals_contract = {
            'name': 'Test Contract Mobile',
            'partner_id': partner_id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref("somconnexio.service_technology_mobile"),
            'service_supplier_id': self.ref("somconnexio.service_supplier_masmovil"),
            'mobile_contract_service_info_id': mobile_contract_service_info.id,
        }
        contract = self.env['contract.contract'].create(vals_contract)
        self.assertTrue(self.parent_partner.has_active_contract)

        contract.write({
            'is_terminated': True
        })

        self.assertFalse(self.parent_partner.has_active_contract)

    def test_does_not_have_active_contract(self):
        self.assertFalse(self.parent_partner.has_active_contract)

    def test_action_view_partner_invoices_only_filter_cancel(self):
        action = self.parent_partner.action_view_partner_invoices()
        domain = action["domain"]
        self.assertIn(
            ('state', 'not in', ['cancel']),
            domain
        )

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_address_one_field_changed_message_post(self, message_post_mock):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        partner.write({'street': "test-new"})
        message_post_mock.assert_called_with(
            body="Contact address has been changed from test to test-new"
        )

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_address_many_field_changed_message_post(self, message_post_mock):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        partner.write({'street': "test-new", 'street2': "test-new-2"})
        message_post_mock.assert_has_calls([
            call(body="Contact address has been changed from test to test-new"),
            call(body="Contact address has been changed from test2 to test-new-2")
        ], any_order=True)

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_address_other_fields_changed_message_post(self, message_post_mock):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        partner.write({"name": 'test-name'})
        message_post_mock.assert_not_called()

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_address_mixed_fields_changed_message_post(self, message_post_mock):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        partner.write({"name": 'test-name', "street": 'test-new'})
        message_post_mock.assert_called_once_with(
            body='Contact address has been changed from test to test-new'
        )

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_address_state_id_changed_message_post(self, message_post_mock):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        partner.write({"state_id": self.ref('base.state_es_m')})
        message_post_mock.assert_called_once_with(
            body='Contact address has been changed from Barcelona to Madrid'
        )

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_address_country_id_changed_message_post(self, message_post_mock):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test2',
            'city': 'test',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'representative'
        })
        partner.write({"country_id": self.ref('base.fr')})
        message_post_mock.assert_called_once_with(
            body='Contact address has been changed from Spain to France'
        )

    def test_not_create_partner_if_vat_exists(self):
        partner_vals = {
            'name': 'test',
            'vat': 'ES39390704F'
        }
        self.env['res.partner'].create(partner_vals)
        self.assertRaisesRegex(
            UserError,
            "A partner with VAT {} already exists in our system".format(partner_vals['vat']), # noqa
            self.env['res.partner'].create,
            partner_vals
        )

    @patch('odoo.addons.somconnexio.models.res_partner.Customer.get') # noqa
    def test_update_customer_one_customer_account(self, CustomerGetMock): # noqa
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'contract-email',
            'ref': '1234',
            'lang': 'es_ES'
        })
        oc_code = "1234_1"
        self.assertTrue(partner)
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = Mock(spect=["customerAccounts", "code"])
        mock_customer.customer.code = partner.ref
        mock_customer.customer.customerAccounts = {
            "customerAccount": [
                {
                    "code": oc_code
                }
            ]
        }

        def side_effect_customer_get(code):
            if code == partner.ref:
                return mock_customer

        CustomerGetMock.side_effect = side_effect_customer_get
        queue_jobs_before = self.env['queue.job'].search([])
        partner.with_context(test_queue_job_no_delay=False).update_accounts_address()
        queue_jobs_after = self.env['queue.job'].search([])
        self.assertEquals(1, len(queue_jobs_after - queue_jobs_before))
        CustomerGetMock.assert_called_once_with(partner.ref)

    @patch('odoo.addons.somconnexio.models.res_partner.Customer.get') # noqa
    def test_update_customer_many_customer_account(self, CustomerGetMock): # noqa
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'contract-email',
            'ref': '1234',
            'lang': 'es_ES'
        })
        oc_codes = ["1234_1", "1234_2"]
        self.assertTrue(partner)
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = Mock(spect=["customerAccounts", "code"])
        mock_customer.customer.code = partner.ref
        mock_customer.customer.customerAccounts = {
            "customerAccount": [
                {
                    "code": oc_codes[0]
                },
                {
                    "code": oc_codes[1]
                }

            ]
        }

        def side_effect_customer_get(code):
            if code == partner.ref:
                return mock_customer

        CustomerGetMock.side_effect = side_effect_customer_get
        queue_jobs_before = self.env['queue.job'].search([])
        partner.with_context(test_queue_job_no_delay=False).update_accounts_address()
        queue_jobs_after = self.env['queue.job'].search([])
        self.assertEquals(2, len(queue_jobs_after - queue_jobs_before))
        CustomerGetMock.assert_called_once_with(partner.ref)

    @patch('odoo.addons.somconnexio.models.res_partner.CRMAccountHierarchyFromPartnerUpdateService')  # noqa
    def test_update_subscription(self, CRMAccountFromPartnerMock):
        partner = self.env['res.partner'].create({
            'parent_id': self.parent_partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'email': 'test@example.com',
            'type': 'contract-email',
            'ref': '1234',
            'lang': 'es_ES'
        })
        oc_code = "1234_1"
        partner.update_subscription('address', oc_code)
        CRMAccountFromPartnerMock.assert_called_once_with(
            partner, "address", oc_code
        )
        CRMAccountFromPartnerMock.return_value.run.assert_called()
