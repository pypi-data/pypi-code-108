from ..sc_test_case import SCTestCase
from ...opencell_models.customer import CustomerFromPartner
from ...opencell_models.opencell_types.description import Description
from ...opencell_models.opencell_types.address import Address

from faker import Faker


class OpenCellConfigurationFake:
    seller_code = 'SC'
    customer_category_code = 'CLIENT'


class CustomerFromPartnerTests(SCTestCase):

    def setUp(self):
        super().setUp()
        fake = Faker('es-ES')
        self.partner = self.env['res.partner'].create({
            'firstname': fake.first_name(),
            'lastname': fake.last_name(),
            'street': fake.street_address(),
            'street2': fake.secondary_address(),
            'zip': fake.postcode(),
            'city': fake.city(),
            'state_id': self.ref('base.state_es_m'),
            'country_id': self.ref('base.es'),
            'vat': fake.nif(),
            'mobile': fake.phone_number(),
            'email': fake.email(),
            'ref': fake.random_int(),
        })
        self.opencell_configuration = OpenCellConfigurationFake()

    # We test the AccountHierarchyResource defined methods in this class
    def test_name_returns_expected_struct(self):
        expected_name = {
            "firstName": self.partner.firstname,
            "lastName": self.partner.lastname
        }
        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(expected_name, customer_from_partner.name)

    def test_description_returns_partner_fullname_as_oc_description_type(self):
        expected_description = Description(self.partner.name).text

        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(expected_description, customer_from_partner.description)

    def test_address_returns_expected_struct(self):
        expected_address = Address(
            address=self.partner.full_street,
            zip=self.partner.zip,
            city=self.partner.city,
            state=self.partner.state_id.name,
            country=self.partner.country_id.code).to_dict()

        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(expected_address, customer_from_partner.address)

    def test_vatNo_returns_partner_vat_code(self):
        expected_vatNo = self.partner.vat

        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(expected_vatNo, customer_from_partner.vatNo)

    def test_seller_returns_opencell_configuration_seller_code(self):
        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(
            self.opencell_configuration.seller_code, customer_from_partner.seller
        )

    def test_email_returns_partner_contact_email(self):
        expected_email = self.partner.email

        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(expected_email, customer_from_partner.email)

    def test_code_returns_partner_ref(self):
        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(self.partner.ref, customer_from_partner.code)

    def test_contactInformation_returns_expected_struct(self):
        expected_contact_info = {
            "email": self.partner.email,
            "mobile": self.partner.mobile,
        }
        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(
            expected_contact_info, customer_from_partner.contactInformation
        )

    def test_customerCategory_returns_category_code(self):
        customer_from_partner = CustomerFromPartner(
            self.partner, self.opencell_configuration
        )

        self.assertEqual(
            self.opencell_configuration.customer_category_code,
            customer_from_partner.customerCategory
        )
