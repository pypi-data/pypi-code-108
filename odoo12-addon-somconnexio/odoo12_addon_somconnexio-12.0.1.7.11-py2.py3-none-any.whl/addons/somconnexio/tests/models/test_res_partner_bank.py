from ..sc_test_case import SCTestCase


class TestResPartnerBankTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

    def test_fill_bank_id_on_create(self):
        new_iban = "ES6621000418401234567891"
        partner_id = self.browse_ref('somconnexio.res_partner_2_demo')

        partner_bank = self.env['res.partner.bank'].create({
            'acc_type': 'iban',
            'acc_number': new_iban,
            'partner_id': partner_id.id
        })

        self.assertEquals(partner_bank.bank_id.name, "Caixabank, S.A.")
