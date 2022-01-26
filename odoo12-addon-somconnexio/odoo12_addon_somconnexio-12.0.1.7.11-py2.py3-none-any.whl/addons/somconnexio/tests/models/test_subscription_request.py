from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class TestSubscription(SCTestCase):

    def setUp(self, *args, **kwargs):
        result = super().setUp(*args, **kwargs)
        self.SubscriptionRequest = self.env['subscription.request']
        crm_lead_pool = self.env['crm.lead']
        vals_lead_a = {
            'name': 'Test Lead a'
        }
        vals_lead_b = {
            'name': 'Test Lead b'
        }
        self.crm_lead_a = crm_lead_pool.create(vals_lead_a)
        self.crm_lead_b = crm_lead_pool.create(vals_lead_b)
        self.vals_subscription = {
            'already_cooperator': False,
            'is_company': False,
            'firstname': 'Manuel',
            'lastname': 'Dublues Test',
            'email': 'manuel@demo-test.net',
            'ordered_parts': 1,
            'address': 'schaerbeekstraat',
            'city': 'Brussels',
            'zip_code': '1111',
            'country_id': self.ref('base.es'),
            'date': datetime.now() - timedelta(days=12),
            'company_id': 1,
            'source': 'manual',
            'share_product_id': False,
            'lang': 'en_US',
            'sponsor_id': False,
            'vat': "53020066Y",
            'iban': 'ES6020808687312159493841'
        }
        CoopAgreement = self.env['coop.agreement']
        vals_coop_agreement = {
            'partner_id': self.ref("easy_my_coop.res_partner_cooperator_1_demo"),
            'products': False,
            'code': 'CODE1',
        }
        self.coop_agreement = CoopAgreement.create(vals_coop_agreement)
        if not self.env.ref('easy_my_coop.sequence_subscription_journal', False):
            journal_sequence = self.env['ir.sequence'].create({
                "name": "Account Default Subscription Journal",
                "padding": 3,
                "prefix": "SUBJ/%(year)s/",
                "use_date_range": True
            })
            self.env['ir.model.data'].create({
                'module': 'easy_my_coop',
                'name': 'sequence_subscription_journal',
                'model': 'ir.sequence',
                'res_id': journal_sequence.id,
                'noupdate': True
            })
        if not self.env.ref('easy_my_coop.subscription_journal', False):
            journal = self.env['account.journal'].create({
                "name": "Subscription Journal",
                "code": "SUBJ",
                "type": "sale",
                "sequence_id": self.ref("easy_my_coop.sequence_subscription_journal")
            })
            self.env['ir.model.data'].create({
                'module': 'easy_my_coop',
                'name': 'subscription_journal',
                'model': 'account.journal',
                'res_id': journal.id,
                'noupdate': True
            })
        if not self.env.ref("easy_my_coop.account_cooperator_demo", False):
            account = self.env['account.account'].create({
                "code": "416101",
                "name": "Cooperators",
                "user_type_id": self.ref("account.data_account_type_receivable"),
                "reconcile": True
            })
            self.env['ir.model.data'].create({
                'module': 'easy_my_coop',
                'name': 'account_cooperator_demo',
                'model': 'account.account',
                'res_id': account.id,
                'noupdate': True
            })
            self.browse_ref('base.main_company').property_cooperator_account = (
                self.browse_ref('easy_my_coop.account_cooperator_demo')
            )
        return result

    def test_create_subscription_coop_agreement_sponsorship(self):
        vals_subscription_sponsorship = self.vals_subscription.copy()
        vals_subscription_sponsorship.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship_coop_agreement',
            'coop_agreement_id': self.coop_agreement.id,
        })
        subscription = self.SubscriptionRequest.create(vals_subscription_sponsorship)
        self.assertEqual(subscription.subscription_amount, 0.0)

    def test_create_subscription_coop_agreement_sponsorship_without_coop_agreement_raise_validation_error(self):  # noqa
        vals_subscription_sponsorship = self.vals_subscription.copy()
        vals_subscription_sponsorship.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship_coop_agreement',
            'coop_agreement_id': False,
        })

        self.assertRaises(
            ValidationError,
            self.SubscriptionRequest.create,
            vals_subscription_sponsorship
        )

    def test_validate_subscription_coop_agreement_sponsorship(self):
        vals_subscription_sponsorship = self.vals_subscription.copy()
        vals_subscription_sponsorship.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship_coop_agreement',
            'coop_agreement_id': self.coop_agreement.id,
        })
        subscription = self.SubscriptionRequest.create(vals_subscription_sponsorship)
        subscription.validate_subscription_request()

        partner = subscription.partner_id
        self.assertEqual(partner.coop_agreement_id.id, self.coop_agreement.id)

        self.assertFalse(partner.coop_candidate)
        self.assertFalse(partner.coop_sponsee)
        self.assertTrue(partner.coop_agreement)

    def test_validate_subscription_nie_wo_nacionality(self):
        vals_subscription_sponsorship = self.vals_subscription.copy()
        vals_subscription_sponsorship.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship_coop_agreement',
            'coop_agreement_id': self.coop_agreement.id,
        })
        vals_subscription_sponsorship.update({
            'vat': 'Z1234567R',
            'nationality': False,
        })
        self.assertRaises(
            ValidationError,
            self.SubscriptionRequest.create,
            vals_subscription_sponsorship
        )

    def test_validate_subscription_nacionality_in_partner(self):
        vals_subscription_sponsorship = self.vals_subscription.copy()
        vals_subscription_sponsorship.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship_coop_agreement',
            'coop_agreement_id': self.coop_agreement.id,
        })
        vals_subscription_sponsorship.update({
            'vat': 'Z1234567R',
            'nationality': self.ref('base.es'),
        })
        subscription = self.SubscriptionRequest.create(
            vals_subscription_sponsorship
        )
        subscription.validate_subscription_request()
        partner = subscription.partner_id
        self.assertEquals(partner.nationality, self.browse_ref('base.es'))

    def test_validate_regular_subscription_bind_partner(self):
        vals_regular_subscription = self.vals_subscription.copy()
        subscription = self.SubscriptionRequest.create(
            vals_regular_subscription
        )
        subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })
        self.crm_lead_a.subscription_request_id = subscription
        subscription.validate_subscription_request()
        partner = self.crm_lead_a.partner_id
        self.assertEquals(partner, subscription.partner_id)

    def test_validate_sponsor_subscription_bind_partner(self):
        vals_sponsor_subscription = self.vals_subscription.copy()
        sponsor_id = self.ref("easy_my_coop.res_partner_cooperator_1_demo")
        vals_sponsor_subscription.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship',
            'sponsor_id': sponsor_id,
        })
        subscription = self.SubscriptionRequest.create(
            vals_sponsor_subscription
        )
        self.crm_lead_a.subscription_request_id = subscription
        subscription.validate_subscription_request()
        partner = self.crm_lead_a.partner_id
        self.assertEquals(partner, subscription.partner_id)

    def test_validate_coop_agreement_subscription_bind_partner(self):
        vals_coop_agreement_subscription = self.vals_subscription.copy()
        vals_coop_agreement_subscription.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship_coop_agreement',
            'coop_agreement_id': self.coop_agreement.id,
        })
        vals_coop_agreement_subscription.update({
            'vat': 'Z1234567R',
            'nationality': self.ref('base.es'),
        })
        subscription = self.SubscriptionRequest.create(
            vals_coop_agreement_subscription
        )
        self.crm_lead_a.subscription_request_id = subscription
        subscription.validate_subscription_request()
        partner = self.crm_lead_a.partner_id
        self.assertEquals(partner, subscription.partner_id)

    def test_validate_different_crm_leads_bind_partner(self):
        vals_regular_subscription = self.vals_subscription.copy()
        vals_different_subscription = self.vals_subscription.copy()
        vals_different_subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })
        vals_regular_subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })
        regular_subscription = self.SubscriptionRequest.create(
            vals_regular_subscription
        )
        different_subscription = self.SubscriptionRequest.create(
            vals_different_subscription
        )
        self.crm_lead_a.subscription_request_id = regular_subscription
        self.crm_lead_b.subscription_request_id = different_subscription
        regular_subscription.validate_subscription_request()
        partner = self.crm_lead_a.partner_id
        self.assertEquals(partner, regular_subscription.partner_id)
        self.assertFalse(self.crm_lead_b.partner_id)

    def test_validate_many_crm_leads_same_bind_partner(self):
        vals_regular_subscription = self.vals_subscription.copy()
        vals_regular_subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })
        regular_subscription = self.SubscriptionRequest.create(
            vals_regular_subscription
        )
        self.crm_lead_a.subscription_request_id = regular_subscription
        self.crm_lead_b.subscription_request_id = regular_subscription
        regular_subscription.validate_subscription_request()
        partner_a = self.crm_lead_a.partner_id
        partner_b = self.crm_lead_b.partner_id
        self.assertEquals(partner_a, regular_subscription.partner_id)
        self.assertEquals(partner_b, regular_subscription.partner_id)

    def test_validate_subscription_error_not_bind(self):
        vals_subscription = self.vals_subscription.copy()
        vals_subscription.update({
            'share_product_id': self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
            'ordered_parts': False,
        })
        subscription = self.SubscriptionRequest.create(
            vals_subscription
        )
        self.crm_lead_a = subscription
        self.assertRaises(
            UserError,
            subscription.validate_subscription_request,
        )
        self.assertFalse(self.crm_lead_a.partner_id)

    def test_validate_subscription_split_in_invoice(self):
        vals_subscription = self.vals_subscription.copy()
        vals_subscription['payment_type'] = 'split'
        vals_subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })
        subscription = self.SubscriptionRequest.create(
            vals_subscription
        )
        subscription.validate_subscription_request()
        self.assertEquals(
            subscription.capital_release_request.payment_term_id,
            self.browse_ref('somconnexio.account_payment_term_10months')
        )

    def test_validate_subscription_not_split_in_invoice(self):
        vals_subscription = self.vals_subscription.copy()
        vals_subscription['payment_type'] = 'single'
        vals_subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })
        subscription = self.SubscriptionRequest.create(
            vals_subscription
        )
        subscription.validate_subscription_request()
        self.assertTrue(
            len(subscription.capital_release_request.payment_term_id) == 0
        )

    def test_validate_subscription_payment_mode_in_invoice(self):
        vals_subscription = self.vals_subscription.copy()
        vals_subscription['payment_type'] = 'single'
        vals_subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })
        subscription = self.SubscriptionRequest.create(
            vals_subscription
        )
        subscription.validate_subscription_request()
        self.assertEquals(
            subscription.capital_release_request.payment_mode_id,
            self.browse_ref('somconnexio.payment_mode_inbound_sepa')
        )

    def test_validate_subscription_with_ES_VAT_not_change_value(self):
        vals_subscription = self.vals_subscription.copy()
        vals_subscription['vat'] = 'ES67793166E'
        vals_subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })

        subscription = self.SubscriptionRequest.create(
            vals_subscription
        )
        subscription.validate_subscription_request()
        self.assertEquals(
            subscription.partner_id.vat,
            vals_subscription['vat']
        )

    def test_validate_organization_subscription(self):
        vals_subscription = self.vals_subscription.copy()
        vals_subscription['is_company'] = True
        vals_subscription['phone'] = '666666666'
        vals_subscription['company_name'] = 'company_name'
        vals_subscription.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
        })
        subscription = self.SubscriptionRequest.create(
            vals_subscription
        )
        subscription.validate_subscription_request()
        self.assertEquals(
            subscription.email,
            vals_subscription['email']
        )
        self.assertEquals(
            subscription.phone,
            vals_subscription['phone']
        )
        self.assertEquals(
            subscription.partner_id.name,
            vals_subscription['company_name']
        )

    def test_validate_subscription_request(self):
        request = self.browse_ref(
            "somconnexio.sc_subscription_request_1_demo"
        )

        # todo missing structure fails the rules?
        request.validate_subscription_request()

        self.assertEquals(request.state, "done")
        self.assertTrue(request.partner_id)
        self.assertTrue(request.partner_id.coop_candidate)
        self.assertFalse(request.partner_id.member)
        self.assertEquals(request.partner_id.type, "representative")
        self.assertEquals(request.type, "new")
        self.assertTrue(len(request.capital_release_request) >= 1)
        self.assertEquals(request.capital_release_request.state, "open")
        self.assertTrue(request.capital_release_request.sent)

    def test_validate_sr_raise_error_if_already_exist_partner_with_same_vat(self):
        request = self.browse_ref(
            "somconnexio.sc_subscription_request_1_demo"
        )
        partner = self.browse_ref(
            "somconnexio.res_partner_1_demo"
        )
        request.vat = partner.vat

        self.assertRaises(
            UserError,
            request.validate_subscription_request
        )

    def test_validate_subscription_request_normalize_vat(self):
        subscription_request = self.browse_ref(
            "somconnexio.sc_subscription_request_1_demo"
        )
        subscription_request["vat"] = "67.793.166-E    "

        # todo missing structure fails the rules?
        subscription_request.validate_subscription_request()

        self.assertEqual(
            subscription_request.partner_id.vat,
            "ES67793166E"
        )

    def test_name_search_vat(self):
        subscription = self.SubscriptionRequest.create(self.vals_subscription)
        name_search_results = self.SubscriptionRequest.name_search(
            name='53020066Y', operator='ilike'
        )
        self.assertTrue(name_search_results)
        self.assertEqual(subscription.id, name_search_results[0][0])

    def test_name_search_name(self):
        subscription = self.SubscriptionRequest.create(self.vals_subscription)
        name_search_results = self.SubscriptionRequest.name_search(
            name='Manuel', operator='ilike'
        )
        self.assertTrue(name_search_results)
        self.assertEqual(subscription.id, name_search_results[0][0])

    def test_name_search_email(self):
        subscription = self.SubscriptionRequest.create(self.vals_subscription)
        name_search_results = self.SubscriptionRequest.name_search(
            name='manuel@demo-test.net', operator='ilike'
        )
        self.assertTrue(name_search_results)
        self.assertEqual(subscription.id, name_search_results[0][0])

    def test_validate_subscription_to_convert_sponsored_in_member(self):
        sponsored_partner = self.browse_ref(
            "somconnexio.res_sponsored_partner_1_demo"
        )
        vals_subscription = {
            'partner_id': sponsored_partner.id,
            'is_company': False,
            'already_cooperator': False,
            'firstname': sponsored_partner.firstname,
            'lastname': sponsored_partner.lastname,
            'email': sponsored_partner.email,
            'ordered_parts': 1,
            'address': sponsored_partner.street,
            'city': sponsored_partner.city,
            'zip_code': sponsored_partner.zip,
            'country_id': sponsored_partner.country_id.id,
            'state_id': sponsored_partner.state_id.id,
            'date': datetime.now() - timedelta(days=12),
            'sponsor_id': False,
            'company_id': 1,
            'source': 'manual',
            'share_product_id': self.ref(
                'somconnexio.cooperator_share_product'
            ),
            'lang': 'ca_ES',
            'iban': 'ES6020808687312159493841'
        }

        subscription_request = self.SubscriptionRequest.create(vals_subscription)
        subscription_request.validate_subscription_request()

        self.assertTrue(sponsored_partner.coop_candidate)
        self.assertFalse(sponsored_partner.coop_sponsee)

    def test_name_content_when_is_company(self):
        vals_subscription_company = self.vals_subscription.copy()
        vals_subscription_company["company_name"] = 'My Little Company'
        vals_subscription_company["is_company"] = True

        subscription_request = self.SubscriptionRequest.create(
            vals_subscription_company
        )

        self.assertEqual(
            subscription_request.name,
            vals_subscription_company["company_name"]
        )

    def test_name_content(self):
        subscription_request = self.SubscriptionRequest.create(self.vals_subscription)

        self.assertEqual(
            subscription_request.name,
            " ".join([
                self.vals_subscription["firstname"],
                self.vals_subscription["lastname"],
            ]).strip()
        )

    def test_company_email_content(self):
        vals_subscription_company = self.vals_subscription.copy()
        vals_subscription_company["company_name"] = 'My Little Company'
        vals_subscription_company["is_company"] = True

        subscription_request = self.SubscriptionRequest.create(
            vals_subscription_company
        )

        self.assertEqual(
            subscription_request.company_email,
            vals_subscription_company["email"]
        )

    def test_validate_subscription_request_raise_error_if_bank_inactive(self):  # noqa
        vals_subscription = self.vals_subscription.copy()
        vals_subscription.update({
            'iban': "ES6621000418401234567891"
        })

        self.browse_ref("l10n_es_partner.res_bank_es_2100").write({"active": False})

        sr = self.SubscriptionRequest.create(vals_subscription)

        self.assertRaises(
            ValidationError,
            sr.validate_subscription_request
        )

        self.browse_ref("l10n_es_partner.res_bank_es_2100").write({"active": True})

    def test_validate_subscription_request_raise_error_if_bank_do_not_exist(self):  # noqa
        vals_subscription = self.vals_subscription.copy()
        vals_subscription.update({
            'iban': "ES66999900418401234567891"
        })

        sr = self.SubscriptionRequest.create(vals_subscription)

        self.assertRaises(
            ValidationError,
            sr.validate_subscription_request
        )

    def test_validate_subscription_coop_agreement_to_member(self):
        vals_subscription_sponsorship = self.vals_subscription.copy()
        vals_subscription_sponsorship.update({
            'share_product_id': False,
            'ordered_parts': False,
            'type': 'sponsorship_coop_agreement',
            'coop_agreement_id': self.coop_agreement.id,
        })
        subscription = self.SubscriptionRequest.create(vals_subscription_sponsorship)
        subscription.validate_subscription_request()
        vals_subscription_membership = self.vals_subscription.copy()
        vals_subscription_membership.update({
            "share_product_id": self.browse_ref(
                "easy_my_coop.product_template_share_type_2_demo"
            ).product_variant_id.id,
            "partner_id": subscription.partner_id.id,
        })
        subscription_membership = self.SubscriptionRequest.create(
            vals_subscription_membership
        )
        subscription_membership.validate_subscription_request()
        self.assertEquals(subscription.partner_id, subscription_membership.partner_id)
        self.assertFalse(subscription.partner_id.coop_agreement)

    def test_validate_subscription_request_raise_error_if_partner_has_active_share_lines(self):  # noqa
        vals_subscription = self.vals_subscription.copy()
        vals_subscription.update({
            'partner_id': self.ref("easy_my_coop.res_partner_cooperator_1_demo"),
        })

        sr = self.SubscriptionRequest.create(vals_subscription)

        self.assertRaises(
            ValidationError,
            sr.validate_subscription_request
        )
