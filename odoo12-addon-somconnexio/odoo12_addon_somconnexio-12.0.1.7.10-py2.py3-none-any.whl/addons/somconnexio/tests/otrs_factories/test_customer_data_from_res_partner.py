from ..sc_test_case import SCTestCase

from ...otrs_factories.customer_data_from_res_partner \
    import CustomerDataFromResPartner


class CustomerDataFromResPartnerTest(SCTestCase):
    def test_build(self):
        partner = self.env.ref('somconnexio.res_partner_2_demo')

        customer_data = CustomerDataFromResPartner(partner).build()

        self.assertEqual(customer_data.id, partner.ref)
        self.assertEqual(customer_data.vat_number, partner.vat)
        self.assertEqual(customer_data.phone, partner.mobile)
        self.assertEqual(customer_data.first_name, partner.firstname)
        self.assertEqual(customer_data.name, partner.lastname)
        self.assertEqual(customer_data.street, partner.full_street)
        self.assertEqual(customer_data.zip, partner.zip)
        self.assertEqual(customer_data.city, partner.city)
        self.assertEqual(customer_data.subdivision, "ES-V")
