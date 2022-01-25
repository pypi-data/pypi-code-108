from ..sc_test_case import SCComponentTestCase


class TestPartnerBankListener(SCComponentTestCase):
    def test_create_mandate_in_partner_bank_creation(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")
        previous_mandate_count = partner.mandate_count

        self.env["res.partner.bank"].create({
            "acc_number": "ES6621000418401234567891",
            "partner_id": partner.id
        })
        partner._compute_mandate_count()

        self.assertEqual(partner.mandate_count, previous_mandate_count+1)

    def test_not_create_mandate_in_partner_bank_creation_if_partner_is_not_customer(self):  # noqa
        partner = self.browse_ref("base.res_partner_4")
        previous_mandate_count = partner.mandate_count
        self.env["res.partner.bank"].create({
            "acc_number": "ES6621000418401234567891",
            "partner_id": partner.id
        })
        partner._compute_mandate_count()

        self.assertEqual(partner.mandate_count, previous_mandate_count)
