from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class TestCreateLeadfromPartnerWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.browse_ref('somconnexio.res_partner_2_demo')
        self.email = self.env['res.partner'].create({
            'parent_id': self.partner.id,
            'email': 'new_email@test.com',
            'type': 'contract-email'
        })
        self.partner.phone = '888888888'

    def test_create_new_mobile_lead(self):
        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test new mobile with invoice address',
            'bank_id': self.partner.bank_ids.id,
            'email_id': self.email.id,
            'product_id': self.ref('somconnexio.SenseMinuts2GB'),
            'service_type': 'mobile',
            'icc': '666',
            'type': 'new',
            'delivery_street': 'Principal A',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
            'invoice_street': 'Principal B',
            'invoice_zip_code': '08015',
            'invoice_city': 'Barcelona',
            'invoice_state_id': self.ref('base.state_es_b'),
        })

        crm_lead_action = wizard.create_lead()
        crm_lead_line = self.env["crm.lead.line"].browse(crm_lead_action["res_id"])
        crm_lead = crm_lead_line.lead_id

        self.assertEquals(crm_lead_action.get('xml_id'),
                          "somconnexio.view_form_lead_line_mobile")

        self.assertEquals(crm_lead.name, "test new mobile with invoice address")
        self.assertEquals(crm_lead.partner_id, self.partner)
        self.assertEquals(
            crm_lead.iban,
            self.partner.bank_ids.sanitized_acc_number
        )
        self.assertEquals(crm_lead.email_from, self.email.email)
        self.assertEquals(crm_lead_line.mobile_isp_info.icc, '666')
        self.assertEquals(crm_lead_line.mobile_isp_info.type, 'new')
        self.assertEquals(
            crm_lead_line.product_id,
            self.browse_ref('somconnexio.SenseMinuts2GB')
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_street,
            'Principal A'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_zip_code,
            '08027'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_city,
            'Barcelona'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_state_id,
            self.browse_ref('base.state_es_b')
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_country_id,
            self.browse_ref('base.es')
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_street,
            'Principal B'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_zip_code,
            '08015'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_city,
            'Barcelona'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_state_id,
            self.browse_ref('base.state_es_b')
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_country_id,
            self.browse_ref('base.es')
        )

    def test_create_portability_mobile_lead(self):
        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test portability mobile',
            'bank_id': self.partner.bank_ids.id,
            'email_id': self.email.id,
            'product_id': self.ref('somconnexio.SenseMinuts2GB'),
            'service_type': 'mobile',
            'icc': '666',
            'type': 'portability',
            'previous_contract_type': 'contract',
            'phone_number': '666666666',
            'donor_icc': '3333',
            'previous_mobile_provider': self.ref('somconnexio.previousprovider4'),
            'previous_owner_vat_number': '52736216E',
            'previous_owner_first_name': 'Firstname test',
            'previous_owner_name': 'Lastname test',
            'delivery_street': 'Principal A',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
        })

        crm_lead_action = wizard.create_lead()
        crm_lead_line = self.env["crm.lead.line"].browse(crm_lead_action["res_id"])
        crm_lead = crm_lead_line.lead_id

        self.assertEquals(crm_lead_action.get('xml_id'),
                          "somconnexio.view_form_lead_line_mobile")

        self.assertEquals(crm_lead.name, "test portability mobile")
        self.assertEquals(crm_lead.partner_id, self.partner)
        self.assertEquals(
            crm_lead.iban,
            self.partner.bank_ids.sanitized_acc_number
        )
        self.assertEquals(crm_lead.email_from, self.email.email)
        self.assertEquals(
            crm_lead_line.product_id,
            self.browse_ref('somconnexio.SenseMinuts2GB')
        )
        self.assertEquals(crm_lead_line.mobile_isp_info.icc, '666')
        self.assertEquals(crm_lead_line.mobile_isp_info.type, 'portability')
        self.assertEquals(
            crm_lead_line.mobile_isp_info.previous_contract_type,
            'contract'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.phone_number,
            '666666666'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.icc_donor,
            '3333'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.previous_provider,
            self.browse_ref('somconnexio.previousprovider4')
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.previous_owner_vat_number,
            'ES52736216E'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.previous_owner_first_name,
            'Firstname test'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.previous_owner_name,
            'Lastname test'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_street,
            'Principal A'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_zip_code,
            '08027'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_city,
            'Barcelona'
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_state_id,
            self.browse_ref('base.state_es_b')
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_country_id,
            self.browse_ref('base.es')
        )

    def test_create_new_BA_lead(self):
        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test new BA',
            'bank_id': self.partner.bank_ids.id,
            'email_id': self.email.id,
            'product_id': self.ref('somconnexio.Fibra600Mb'),
            'service_type': 'BA',
            'type': 'new',
            'delivery_street': 'Principal A',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
            'service_street': 'Principal B',
            'service_zip_code': '00123',
            'service_city': 'Barcelona',
            'service_state_id': self.ref('base.state_es_b'),
        })

        crm_lead_action = wizard.create_lead()
        crm_lead_line = self.env["crm.lead.line"].browse(crm_lead_action["res_id"])
        crm_lead = crm_lead_line.lead_id

        self.assertEquals(crm_lead_action.get('xml_id'),
                          "somconnexio.view_form_lead_line_broadband")

        self.assertEquals(crm_lead.name, "test new BA")
        self.assertEquals(crm_lead.partner_id, self.partner)
        self.assertEquals(
            crm_lead.iban,
            self.partner.bank_ids.sanitized_acc_number
        )
        self.assertEquals(crm_lead.email_from, self.email.email)
        self.assertEquals(
            crm_lead_line.product_id,
            self.browse_ref('somconnexio.Fibra600Mb')
        )
        self.assertEquals(crm_lead_line.broadband_isp_info.type, 'new')
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_street,
            'Principal B'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_zip_code,
            '00123'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_city,
            'Barcelona'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_state_id,
            self.browse_ref('base.state_es_b')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_country_id,
            self.browse_ref('base.es')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_street,
            'Principal A'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_zip_code,
            '08027'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_city,
            'Barcelona'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_state_id,
            self.browse_ref('base.state_es_b')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_country_id,
            self.browse_ref('base.es')
        )

    def test_create_portability_BA_lead(self):
        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test BA portability',
            'bank_id': self.partner.bank_ids.id,
            'email_id': self.email.id,
            'product_id': self.ref('somconnexio.Fibra600Mb'),
            'service_type': 'BA',
            'type': 'portability',
            'previous_owner_vat_number': '52736216E',
            'previous_owner_first_name': 'Test',
            'previous_owner_name': 'Test',
            'keep_landline': True,
            'landline': '972972972',
            'previous_BA_service': "fiber",
            'previous_BA_provider': self.ref('somconnexio.previousprovider3'),
            'service_street': 'Principal A',
            'service_zip_code': '00123',
            'service_city': 'Barcelona',
            'service_state_id': self.ref('base.state_es_b'),
            'delivery_street': 'Principal B',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
        })

        crm_lead_action = wizard.create_lead()
        crm_lead_line = self.env["crm.lead.line"].browse(crm_lead_action["res_id"])
        crm_lead = crm_lead_line.lead_id

        self.assertEquals(crm_lead_action.get('xml_id'),
                          "somconnexio.view_form_lead_line_broadband")

        self.assertEquals(crm_lead.name, "test BA portability")
        self.assertEquals(crm_lead.partner_id, self.partner)
        self.assertEquals(
            crm_lead.iban,
            self.partner.bank_ids.sanitized_acc_number
        )
        self.assertEquals(crm_lead.email_from, self.email.email)
        self.assertEquals(
            crm_lead_line.product_id,
            self.browse_ref('somconnexio.Fibra600Mb')
        )
        self.assertEquals(crm_lead_line.broadband_isp_info.type, 'portability')
        self.assertTrue(crm_lead_line.broadband_isp_info.keep_phone_number)
        self.assertEquals(
            crm_lead_line.broadband_isp_info.previous_provider,
            self.browse_ref('somconnexio.previousprovider3')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.previous_service,
            'fiber'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_street,
            'Principal A'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_zip_code,
            '00123'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_city,
            'Barcelona'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_state_id,
            self.browse_ref('base.state_es_b')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_country_id,
            self.browse_ref('base.es')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_street,
            'Principal B'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_zip_code,
            '08027'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_city,
            'Barcelona'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_state_id,
            self.browse_ref('base.state_es_b')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.delivery_country_id,
            self.browse_ref('base.es')
        )

    def test_create_portability_mobile_without_phone_number(self):
        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test portability mobile',
            'bank_id': self.partner.bank_ids.id,
            'email_id': self.email.id,
            'product_id': self.ref('somconnexio.SenseMinuts2GB'),
            'service_type': 'mobile',
            'icc': '666',
            'type': 'portability',
            'previous_contract_type': 'contract',
            'donor_icc': '3333',
            'previous_mobile_provider': self.ref('somconnexio.previousprovider4'),
            'previous_owner_vat_number': '52736216E',
            'previous_owner_first_name': 'Firstname test',
            'previous_owner_name': 'Lastname test',
            'delivery_street': 'Principal A',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
        })

        self.assertRaises(
            ValidationError,
            wizard.create_lead
        )

    def test_create_portability_ba_keep_landline_without_number(self):
        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test BA portability',
            'bank_id': self.partner.bank_ids.id,
            'email_id': self.email.id,
            'phone_contact': '888888888',
            'product_id': self.ref('somconnexio.Fibra600Mb'),
            'service_type': 'BA',
            'type': 'portability',
            'previous_owner_vat_number': '52736216E',
            'previous_owner_first_name': 'Test',
            'previous_owner_name': 'Test',
            'keep_landline': True,
            'previous_BA_service': "adsl",
            'previous_BA_provider': self.ref('somconnexio.previousprovider3'),
            'service_street': 'Principal A',
            'service_zip_code': '00123',
            'service_city': 'Barcelona',
            'service_state_id': self.ref('base.state_es_b'),
            'service_country_id': self.ref('base.es'),
            'delivery_street': 'Principal B',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
            'delivery_country_id': self.ref('base.es'),
        })

        self.assertRaises(
            ValidationError,
            wizard.create_lead
        )

    def test_set_phone_to_partner_if_none(self):
        self.partner.phone = False
        self.partner.mobile = False

        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test new mobile with invoice address',
            'bank_id': self.partner.bank_ids.id,
            'email_id': self.partner.id,
            'phone_contact': '888888888',
            'product_id': self.ref('somconnexio.SenseMinuts2GB'),
            'service_type': 'mobile',
            'icc': '666',
            'type': 'new',
            'delivery_street': 'Principal A',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
            'invoice_street': 'Principal B',
            'invoice_zip_code': '08015',
            'invoice_city': 'Barcelona',
            'invoice_state_id': self.ref('base.state_es_b'),
        })

        self.assertFalse(self.partner.phone)

        crm_lead_action = wizard.create_lead()
        crm_lead_line = self.env["crm.lead.line"].browse(crm_lead_action["res_id"])

        self.assertEqual(self.partner.phone, wizard.phone_contact)
        self.assertEqual(crm_lead_line.lead_id.phone, wizard.phone_contact)

    def test_default_phone_contact_partner_mobile_over_phone(self):
        self.partner.mobile = '666777888'
        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test new mobile with invoice address',
            'bank_id': self.partner.bank_ids.id,
            'email_id': self.partner.id,
            'product_id': self.ref('somconnexio.SenseMinuts2GB'),
            'service_type': 'mobile',
            'icc': '666',
            'type': 'new',
            'delivery_street': 'Principal A',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
            'invoice_street': 'Principal B',
            'invoice_zip_code': '08015',
            'invoice_city': 'Barcelona',
            'invoice_state_id': self.ref('base.state_es_b'),
        })
        crm_lead_action = wizard.create_lead()
        crm_lead_line = self.env["crm.lead.line"].browse(crm_lead_action["res_id"])

        self.assertEqual(wizard.phone_contact, self.partner.mobile)
        self.assertEqual(wizard.phone_contact, crm_lead_line.lead_id.phone)

    def test_products_filtered_when_partner_has_coop_agreement(self):
        self.partner = self.browse_ref(
            'somconnexio.res_sponsored_partner_2_demo'
        )
        self.bank = self.env['res.partner.bank'].create({
            'acc_number': 'ES1720852066623456789011',
            'partner_id': self.partner.id
        })
        self.coop_agreement = self.browse_ref('somconnexio.coop_agreement_1_demo')
        product_templs = self.coop_agreement.products
        self.available_categories = [p.categ_id.id for p in product_templs]

        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test',
            'bank_id': self.bank.id,
            'email_id': self.email.id,
            'phone_contact': '888888888',
            'product_id': self.ref('somconnexio.ADSL20MB1000MinFix'),
            'service_type': 'BA',
            'type': 'new',
            'service_street': 'Principal A',
            'service_zip_code': '00123',
            'service_city': 'Barcelona',
            'service_state_id': self.ref('base.state_es_b'),
            'delivery_street': 'Principal B',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
        })

        self.assertEquals(
            wizard.available_product_templates,
            self.env['product.template'].search([
                ('categ_id', 'in', self.available_categories)
            ])
        )

    def test_products_filtered_when_partner_coop_sponsee(self):
        self.partner = self.browse_ref('somconnexio.res_sponsored_partner_2_demo')
        self.bank = self.env['res.partner.bank'].create({
            'acc_number': 'ES1720852066623456789011',
            'partner_id': self.partner.id
        })
        self.coop_agreement = self.browse_ref('somconnexio.coop_agreement_1_demo')
        product_templs = self.coop_agreement.products
        self.available_categories = [p.categ_id.id for p in product_templs]

        wizard = self.env['partner.create.lead.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'opportunity': 'test',
            'bank_id': self.bank.id,
            'email_id': self.email.id,
            'phone_contact': '888888888',
            'product_id': self.ref('somconnexio.SenseMinuts2GB'),
            'service_type': 'mobile',
            'type': 'new',
            'service_street': 'Principal A',
            'service_zip_code': '00123',
            'service_city': 'Barcelona',
            'service_state_id': self.ref('base.state_es_b'),
            'delivery_street': 'Principal B',
            'delivery_zip_code': '08027',
            'delivery_city': 'Barcelona',
            'delivery_state_id': self.ref('base.state_es_b'),
        })

        self.assertEquals(
            wizard.available_product_templates,
            self.env['product.template'].search([
                ('categ_id', 'in', self.available_categories)
            ])
        )
