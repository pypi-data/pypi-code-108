from ..sc_test_case import SCTestCase
from ...opencell_models.crm_account_hierarchy import \
    CRMAccountHierarchyFromContract, CRMAccountHierarchyFromPartner

from faker import Faker


class OpenCellConfigurationFake:
    seller_code = 'SC'
    customer_category_code = 'CLIENT'


class CRMAccountHierarchyTests(SCTestCase):

    def setUp(self):
        super().setUp()
        fake = Faker('es-ES')
        self.res_partner_bank = {
            'bank_id': self.ref('base.bank_ing'),
            'acc_number': "ES7921000813610123456789",
        }
        self.fake_mobile_phone = '696696696'

        self.partner = self.env['res.partner'].create({
            'name': fake.first_name(),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'street': fake.street_address(),
            'street2': fake.secondary_address(),
            'zip': fake.postcode(),
            'city': fake.city(),
            'state_id': self.ref('base.state_es_m'),
            'country_id': self.ref('base.es'),
            'vat': fake.nif(),
            'mobile': self.fake_mobile_phone,
            'email': 'fake@email.com',
            'lang': "ca_ES",
            'bank_ids': [(0, 0, self.res_partner_bank)]
        })
        self.mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': self.partner.bank_ids[0].id,
            })

        child_email = self.env['res.partner'].create({
            'name': 'Partner email',
            'email': 'hello@example.com',
            'parent_id': self.partner.id,
            'type': 'contract-email'
        })
        second_child_email = self.env['res.partner'].create({
            'name': 'Partner second email',
            'email': 'second@example.com',
            'parent_id': self.partner.id,
            'type': 'contract-email'
        })
        third_child_email = self.env['res.partner'].create({
            'name': 'Partner second email',
            'email': 'third@example.com',
            'parent_id': self.partner.id,
            'type': 'contract-email'
        })
        self.contract_line = {
            "name": "Hola",
            "product_id": self.browse_ref('somconnexio.150Min1GB').id,
            "date_start": '2020-01-01'
        }
        service_tech = self.browse_ref('somconnexio.service_technology_mobile')
        service_supplier = self.browse_ref('somconnexio.service_supplier_masmovil')
        self.mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'icc': '123'
        })
        self.contract = self.env['contract.contract'].create({
            "name": "Test Contract",
            "partner_id": self.partner.id,
            "code": 1234,
            "invoice_partner_id": self.partner.id,
            "service_technology_id": service_tech.id,
            "service_supplier_id": service_supplier.id,
            "mobile_contract_service_info_id": self.mobile_contract_service_info.id,
            "contract_line_ids": [(0, 0, self.contract_line)],
            'email_ids': [(4, child_email.id, False)],
            "mandate_id": self.mandate.id,
        })
        self.contract_with_3_emails = self.env['contract.contract'].create({
            "name": "Test Contract",
            "partner_id": self.partner.id,
            "code": 1234,
            "invoice_partner_id": self.partner.id,
            "service_technology_id": service_tech.id,
            "service_supplier_id": service_supplier.id,
            "mobile_contract_service_info_id": self.mobile_contract_service_info.id,
            "contract_line_ids": [(0, 0, self.contract_line)],
            "email_ids": [
                (6, 0, ([child_email.id, second_child_email.id, third_child_email.id]))
            ],
            "mandate_id": self.mandate.id,
        })
        self.opencell_configuration = OpenCellConfigurationFake()

        self.crm_account_hierarchy = CRMAccountHierarchyFromContract(
            self.contract, "Code"
        )

        self.crm_account_hierarchy_from_partner = CRMAccountHierarchyFromPartner(
            self.partner, "Code"
        )

    def test_email(self):
        self.assertEqual(
            self.contract.email_ids.email,
            self.crm_account_hierarchy.email)
        self.assertIsNone(self.crm_account_hierarchy.ccedEmails)

    def test_multiple_emails(self):
        self.assertEqual(len(self.contract_with_3_emails.email_ids), 3)

        crm_account_hierarchy = CRMAccountHierarchyFromContract(
            self.contract_with_3_emails, "Code"
        )
        self.assertEqual(
            crm_account_hierarchy.email,
            self.contract_with_3_emails.email_ids[0].email)
        self.assertIn(
            self.contract_with_3_emails.email_ids[1].email,
            crm_account_hierarchy.ccedEmails)
        self.assertIn(
            self.contract_with_3_emails.email_ids[2].email,
            crm_account_hierarchy.ccedEmails)

    def test_contact_information(self):
        expected_contact_information = {
            "email" : "hello@example.com",
            "phone" : "",
            "mobile" : self.fake_mobile_phone,
            "fax" : ""
        }
        self.assertEqual(
            self.crm_account_hierarchy.contactInformation,
            expected_contact_information
        )

    def test_code(self):
        self.assertEqual(
            "Code",
            self.crm_account_hierarchy.code)

    def test_crmAccountType(self):
        self.assertEqual(
            "CA_UA",
            self.crm_account_hierarchy.crmAccountType)

    def test_phone(self):
        self.assertEqual(
            self.contract.partner_id.mobile,
            self.crm_account_hierarchy.phone)

    def test_crmParentCode(self):
        self.assertEqual(
            self.contract.partner_id.ref,
            self.crm_account_hierarchy.crmParentCode)

    def test_language(self):
        self.assertEqual(
            "CAT",
            self.crm_account_hierarchy.language)

    def test_customerCategory(self):
        self.assertEqual(
            "CLIENT",
            self.crm_account_hierarchy.customerCategory)

    def test_currency(self):
        self.assertEqual(
            "EUR",
            self.crm_account_hierarchy.currency)

    def test_billingCycle(self):
        self.assertEqual(
            "BC_SC_MONTHLY_1ST",
            self.crm_account_hierarchy.billingCycle)

    def test_country(self):
        self.assertEqual("SP", self.crm_account_hierarchy.country)

    def test_electronicBilling(self):
        self.assertTrue(self.crm_account_hierarchy.electronicBilling)

    def test_mailingType(self):
        self.assertEqual("Manual", self.crm_account_hierarchy.mailingType)

    def test_emailTemplate(self):
        self.assertEqual(
            "EMAIL_TEMPLATE_TEST",
            self.crm_account_hierarchy.emailTemplate)

    def test_methodOfPayment(self):
        bank_coordinates = self.crm_account_hierarchy.methodOfPayment[0].get(
            'bankCoordinates')

        self.assertEqual(
            self.contract.mandate_id.partner_bank_id.id,
            self.crm_account_hierarchy.methodOfPayment[0].get('mandateIdentification'))
        self.assertEqual(
            self.contract.mandate_id.partner_bank_id.sanitized_acc_number,
            bank_coordinates.get('iban'))
        self.assertEqual(
            self.contract.mandate_id.partner_bank_id.bank_id.bic,
            bank_coordinates.get('bic'))
        self.assertEqual(
            self.contract.mandate_id.partner_bank_id.bank_id.name,
            bank_coordinates.get('bankName'))
        self.assertEqual(
            "{} {}".format(self.partner.firstname, self.partner.lastname),
            bank_coordinates.get('accountOwner'))


class CRMAccountHierarchyFromPartnerTests(SCTestCase):

    def setUp(self):
        super().setUp()
        fake = Faker('es-ES')
        self.res_partner_bank = {
            'bank_id': self.ref('base.bank_ing'),
            'acc_number': "ES7921000813610123456789",
        }
        self.fake_mobile_phone = '696696696'

        self.partner = self.env['res.partner'].create({
            'name': fake.first_name(),
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'street': fake.street_address(),
            'street2': fake.secondary_address(),
            'zip': fake.postcode(),
            'city': fake.city(),
            'state_id': self.ref('base.state_es_m'),
            'country_id': self.ref('base.es'),
            'vat': fake.nif(),
            'mobile': self.fake_mobile_phone,
            'email': 'fake@email.com',
            'lang': "ca_ES",
            'bank_ids': [(0, 0, self.res_partner_bank)]
        })

        self.crm_account_hierarchy = CRMAccountHierarchyFromPartner(
            self.partner, "Code"
        )

    def test_address(self):
        expected_address_format = {
            "address1": self.partner.full_street,
            "zipCode": self.partner.zip,
            "city": self.partner.city,
            "state": self.partner.state_id.name,
            "country": self.partner.country_id.code,
        }
        self.assertEqual(
            expected_address_format,
            self.crm_account_hierarchy.address
        )

    def test_currency(self):
        self.assertEqual(
            "EUR",
            self.crm_account_hierarchy.currency)

    def test_code(self):
        self.assertEqual(
            "Code",
            self.crm_account_hierarchy.code)

    def test_crmAccountType(self):
        self.assertEqual(
            "CA_UA",
            self.crm_account_hierarchy.crmAccountType)

    def test_language(self):
        self.assertEqual(
            "CAT",
            self.crm_account_hierarchy.language)

    def test_canary_country_code(self):
        self.partner.state_id = self.ref('base.state_es_tf')
        crm_account_hierarchy = CRMAccountHierarchyFromPartner(
            self.partner, "Code"
        )
        self.assertEqual(crm_account_hierarchy.country, 'ES_CN')
        self.partner.state_id = self.ref('base.state_es_gc')
        crm_account_hierarchy = CRMAccountHierarchyFromPartner(
            self.partner, "Code"
        )
        self.assertEqual(crm_account_hierarchy.country, 'ES_CN')

    def test_canary_country_code_is_in_from_partner_to_dict(self):
        self.partner.state_id = self.ref('base.state_es_tf')
        crm_account_hierarchy = CRMAccountHierarchyFromPartner(
            self.partner, "Code"
        )
        crm_account_hierarchy_dict = crm_account_hierarchy.to_dict()
        self.assertIn('country', crm_account_hierarchy_dict)
        self.assertEqual(crm_account_hierarchy_dict['country'], 'ES_CN')
        self.partner.state_id = self.ref('base.state_es_gc')
        crm_account_hierarchy = CRMAccountHierarchyFromPartner(
            self.partner, "Code"
        )
        crm_account_hierarchy_dict = crm_account_hierarchy.to_dict()
        self.assertIn('country', crm_account_hierarchy_dict)
        self.assertEqual(crm_account_hierarchy_dict['country'], 'ES_CN')
