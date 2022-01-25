from datetime import date
from mock import patch, Mock, ANY

from ..sc_test_case import SCTestCase
from ...services.change_partner_emails import ChangePartnerEmails


class ChangePartnerEmailsTests(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.partner = self.browse_ref('base.partner_demo')
        partner_id = self.partner.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_vodafone"
            ),
            'vodafone_fiber_service_contract_info_id': (
                self.vodafone_fiber_contract_service_info.id
            ),
            'bank_id': self.partner.bank_ids.id,
            'email_ids': [(4, self.partner.id, 0)]
        }
        self.contract = self.env['contract.contract'].create(vals_contract)
        vals_contract_same_partner = vals_contract.copy()
        vals_contract_same_partner.update({
            'name': 'Test Contract Broadband B'
        })
        self.contract_same_partner = self.env['contract.contract'].create(
            vals_contract_same_partner
        )
        self.partner_email_b = self.env['res.partner'].create({
            'name': 'Email b',
            'email': 'email_b@example.org',
            'type': 'contract-email',
            'parent_id': self.partner.id
        })
        self.activity_args = {
            'res_model_id': self.ref('contract.model_contract_contract'),
            'user_id': self.ref('base.user_admin'),
            'activity_type_id': self.ref('somconnexio.mail_activity_type_contract_data_change'),  # noqa
            'date_done': date.today(),
            'date_deadline': date.today(),
            'summary': 'Summary',
            'location': 'Location',
            'note': 'Note',
            'done': True,
        }

    @patch(
        'odoo.addons.somconnexio.models.contract.CRMAccountHierarchyFromContractUpdateService',  # noqa
        return_value=Mock(spec=["run"])
    )
    def test_change_contracts_emails_one_email_change_ok(self, MockUpdateService):
        contracts = [self.contract_same_partner, self.contract]
        emails = [self.partner_email_b]

        ChangePartnerEmails(self.env, self.partner).change_contracts_emails(
            contracts,
            emails,
            self.activity_args
        )
        self.assertEquals(self.contract_same_partner.email_ids, self.partner_email_b)
        self.assertEquals(self.contract.email_ids, self.partner_email_b)

        MockUpdateService.assert_called_once_with(
            contracts,
            "email"
        )
        MockUpdateService.return_value.run.assert_called_once_with()

    @patch(
        'odoo.addons.somconnexio.models.contract.CRMAccountHierarchyFromContractUpdateService',  # noqa
        return_value=Mock(spec=["run"])
    )
    def test_change_contracts_emails_many_email_change_ok(self, MockUpdateService):
        contracts = [self.contract_same_partner, self.contract]
        emails = [self.partner_email_b, self.partner]

        ChangePartnerEmails(self.env, self.partner).change_contracts_emails(
            contracts,
            emails,
            self.activity_args
        )

        self.assertIn(self.partner, self.contract.email_ids)
        self.assertIn(self.partner_email_b, self.contract.email_ids)
        self.assertIn(self.partner, self.contract_same_partner.email_ids)
        self.assertIn(self.partner_email_b, self.contract_same_partner.email_ids)

        MockUpdateService.assert_called_once_with(
            contracts,
            "email"
        )
        MockUpdateService.return_value.run.assert_called_once_with()

    @patch(
        'odoo.addons.somconnexio.models.contract.CRMAccountHierarchyFromContractUpdateService',  # noqa
        return_value=Mock(spec=["run"])
    )
    def test_change_contracts_emails_activity_register(
            self, MockUpdateService):
        contracts = [self.contract_same_partner]
        emails = [self.partner_email_b, self.partner]

        mail_activities_before = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)]
        )

        ChangePartnerEmails(self.env, self.partner).change_contracts_emails(
            contracts,
            emails,
            self.activity_args
        )

        mail_activities_after = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)]
        )

        self.assertEquals(len(mail_activities_after) - len(mail_activities_before), 1)

        email_change = mail_activities_after[-1]
        self.assertEquals(email_change.user_id.id, self.activity_args['user_id'])
        self.assertEquals(email_change.summary, self.activity_args['summary'])
        self.assertEquals(
            email_change.activity_type_id.id,
            self.activity_args['activity_type_id']
        )
        self.assertEquals(email_change.done, self.activity_args['done'])
        self.assertEquals(email_change.res_id, self.contract_same_partner.id)

    def test_change_contact_email(self):
        self.assertNotEquals(self.partner.email, self.partner_email_b.email)
        self.assertEqual(self.contract.email_ids[0].email, self.partner.email)

        ChangePartnerEmails(self.env, self.partner).change_contact_email(
            self.partner_email_b
        )

        self.assertEquals(self.partner.email, self.partner_email_b.email)
        self.assertNotEqual(self.contract.email_ids[0].email, self.partner.email)

    @patch(
        'odoo.addons.somconnexio.services.change_partner_emails.SomOfficeUser',  # noqa
        return_value=Mock(spec=["change_email"])
    )
    def test_change_somoffice_email(self, MockSomOfficeUser):
        ChangePartnerEmails(self.env, self.partner).change_somoffice_email(
            self.partner_email_b
        )

        MockSomOfficeUser.assert_called_once_with(
            self.partner.ref,
            ANY,
            self.partner.vat,
            ANY,
        )
        MockSomOfficeUser.return_value.change_email.assert_called_once_with(
            self.partner_email_b.email,
        )

    def test_search_or_create_email_single_result(self):
        self.env['res.partner'].create({
            'name': 'Copy Email',
            'email': self.partner.email,
            'type': 'contract-email',
            'parent_id': self.partner.id
        })
        # Create a duplicated child email
        self.env['res.partner'].create({
            'name': 'Copy Email',
            'email': self.partner.email,
            'type': 'contract-email',
            'parent_id': self.partner.id
        })

        old_email = ChangePartnerEmails(
            self.env, self.partner)._search_or_create_email()

        self.assertEquals(len(old_email), 1)
