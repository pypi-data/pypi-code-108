from ..sc_test_case import SCTestCase


class TestCreateSubscriptionFromPartnerWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.env['res.partner'].create({
            "street": "Street",
            "zip": "1234",
            "city": "City",
            "country_id": self.ref('base.es'),
            "lang": self.browse_ref('base.lang_es').code,
            "company_name": "Test partner company",
            "email": "test@example.com",
            "name": "Test partner company",
            "vat": "ESA46191557",
            "is_company": True,
        })
        self.bank = self.env['res.partner.bank'].create({
            'acc_number': 'ES1720852066623456789011',
            'partner_id': self.partner.id
        })
        self.payment_type = 'single'
        self.share_product = self.browse_ref(
            "easy_my_coop.product_template_share_type_2_demo"
        ).product_variant_id

    def test_create_subscription_from_company_partner_wizard(self):
        wizard = self.env['partner.create.subscription'].create({
            'cooperator': self.partner.id,
            "share_product": self.share_product.id,
            "share_qty": 1,
            "email": "test@example.com",
            "bank_id": self.bank.id,
            "bank_account": self.partner.bank_ids.acc_number,
            "payment_type": self.payment_type,
            "is_company": True
        })
        sub_req = self.env['subscription.request'].browse(
            wizard.create_subscription()['res_id']
        )
        self.assertEquals(sub_req.partner_id, self.partner)
        self.assertEquals(sub_req.share_product_id, self.share_product)
        self.assertEquals(sub_req.ordered_parts, 1)
        self.assertEquals(sub_req.user_id.id, self.env.uid)
        self.assertEquals(sub_req.email, self.partner.email)
        self.assertEquals(sub_req.vat, self.partner.vat)
        self.assertEquals(sub_req.source, "crm")
        self.assertEquals(sub_req.address, self.partner.street)
        self.assertEquals(sub_req.zip_code, self.partner.zip)
        self.assertEquals(sub_req.city, self.partner.city)
        self.assertEquals(sub_req.country_id, self.partner.country_id)
        self.assertEquals(sub_req.lang, self.partner.lang)
        self.assertEquals(sub_req.company_name, self.partner.name)
        self.assertEquals(sub_req.company_email, self.partner.email)
        self.assertEquals(sub_req.name, self.partner.name)
        self.assertTrue(sub_req.is_company)
        self.assertEquals(sub_req.iban, self.bank.acc_number)
        self.assertEquals(sub_req.payment_type, self.payment_type)

    def test_create_subscription_from_person_partner_wizard(self):
        self.partner.name = 'Partner'
        self.partner.firstname = "Joe"
        self.partner.lastname = "Smith"
        wizard = self.env['partner.create.subscription'].create({
            'cooperator': self.partner.id,
            "share_product": self.share_product.id,
            "share_qty": 1,
            "email": "test@example.com",
            "bank_id": self.bank.id,
            "bank_account": self.partner.bank_ids.acc_number,
            "payment_type": self.payment_type,
            "is_company": False
        })
        sub_req = self.env['subscription.request'].browse(
            wizard.create_subscription()['res_id']
        )
        self.assertEquals(sub_req.partner_id, self.partner)
        self.assertEquals(sub_req.share_product_id, self.share_product)
        self.assertEquals(sub_req.ordered_parts, 1)
        self.assertEquals(sub_req.user_id.id, self.env.uid)
        self.assertEquals(sub_req.email, self.partner.email)
        self.assertEquals(sub_req.source, "crm")
        self.assertEquals(sub_req.address, self.partner.street)
        self.assertEquals(sub_req.zip_code, self.partner.zip)
        self.assertEquals(sub_req.city, self.partner.city)
        self.assertEquals(sub_req.country_id, self.partner.country_id)
        self.assertEquals(sub_req.lang, self.partner.lang)
        self.assertEquals(sub_req.firstname, self.partner.firstname)
        self.assertEquals(sub_req.lastname, self.partner.lastname)
        self.assertEquals(sub_req.name, self.partner.name)
        self.assertFalse(sub_req.is_company)
        self.assertEquals(sub_req.iban, self.bank.acc_number)
        self.assertEquals(sub_req.payment_type, self.payment_type)
