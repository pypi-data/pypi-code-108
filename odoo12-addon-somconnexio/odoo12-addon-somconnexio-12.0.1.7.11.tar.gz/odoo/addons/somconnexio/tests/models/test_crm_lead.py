from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class CRMLeadTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.partner_id = self.browse_ref('somconnexio.res_partner_2_demo')
        self.crm_lead_iban = 'ES6000491500051234567891'
        self.crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
            }]
        )

    def test_crm_lead_action_set_won(self):
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'stage_id': self.browse_ref('crm.stage_lead3').id,
            }]
        )
        crm_lead.action_set_won()
        self.assertEquals(crm_lead.stage_id, self.browse_ref('crm.stage_lead4'))

    def test_crm_lead_action_set_won_raise_error_if_not_in_remesa_stage(self):
        self.assertNotEqual(self.crm_lead.stage_id, self.browse_ref('crm.stage_lead3'))
        self.assertRaisesRegex(
            ValidationError,
            "The crm lead must be in remesa stage.",
            self.crm_lead.action_set_won
        )

    def test_crm_lead_action_set_remesa_raise_error_if_not_in_new_stage(self):
        self.crm_lead.write(
            {
                'iban': 'ES91 2100 0418 4502 0005 1332',
                'stage_id': self.browse_ref('crm.stage_lead4').id,
            })
        self.assertNotEqual(self.crm_lead.stage_id, self.browse_ref('crm.stage_lead1'))
        self.assertRaisesRegex(
            ValidationError,
            "The crm lead must be in new stage.",
            self.crm_lead.action_set_remesa
        )

    def test_crm_lead_action_validation_error_crm_lead_with_multiple_lines(self):
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'new',
        })
        mobile_crm_lead_line_1 = self.env['crm.lead.line'].create({
            'name': 'lead line 1',
            'partner': self.partner_id.id,
            'product_id': self.ref('somconnexio.SenseMinuts500MB'),
            'mobile_isp_info': mobile_isp_info.id,
        })
        mobile_crm_lead_line_2 = self.env['crm.lead.line'].create({
            'name': 'lead line 2',
            'partner': self.browse_ref('somconnexio.res_partner_1_demo').id,
            'product_id': self.ref('somconnexio.SenseMinuts500MB'),
            'mobile_isp_info': mobile_isp_info.id,
        })

        self.crm_lead.write({
            'lead_line_ids': [(6, False, [mobile_crm_lead_line_1.id,
                                          mobile_crm_lead_line_2.id])]
        })
        self.assertNotEqual(self.crm_lead.stage_id, self.browse_ref('crm.stage_lead4'))

        self.assertRaises(
            ValidationError,
            self.crm_lead.action_set_won
        )

    def test_ensure_crm_lead_iban_in_partner(self):
        self.crm_lead.write(
            {
                'iban': self.crm_lead_iban,
                'stage_id': self.browse_ref('crm.stage_lead3').id,
            })

        self.assertEquals(len(self.partner_id.bank_ids), 1)
        self.assertNotEqual(self.crm_lead_iban,
                            self.partner_id.bank_ids[0].sanitized_acc_number)

        self.crm_lead.action_set_won()

        self.assertEquals(len(self.partner_id.bank_ids), 2)
        self.assertEquals(self.crm_lead_iban,
                          self.partner_id.bank_ids[1].sanitized_acc_number)

    def test_crm_lead_partner_email(self):
        self.assertEquals(self.crm_lead.email_from, self.partner_id.email)

    def test_crm_lead_subscription_request_email(self):
        subscription_request_id = self.browse_ref(
            'somconnexio.sc_subscription_request_2_demo')

        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'New Test Lead',
                'subscription_request_id': subscription_request_id.id,
            }]
        )
        self.assertEquals(crm_lead.email_from, subscription_request_id.email)

    def test_crm_lead_new_email(self):
        new_email = "new.email@demo.net"
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'New Test Lead',
                'partner_id': self.partner_id.id,
                'email_from': new_email,
            }]
        )
        self.assertEquals(crm_lead.email_from, new_email)

    def test_crm_lead_action_set_remesa(self):
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'new',
        })
        product_mobile = self.env.ref(
            "somconnexio.100MinSenseDades_product_template"
        ).product_variant_id
        lead_line_vals = {
            'name': '666666666',
            'product_id': product_mobile.id,
            'mobile_isp_info': mobile_isp_info.id,
        }
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
            }]
        )
        crm_lead.action_set_remesa()
        self.assertEquals(crm_lead.stage_id, self.browse_ref('crm.stage_lead3'))

    def test_crm_lead_action_set_remesa_raise_error_without_partner(self):
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'new',
        })
        product_mobile = self.env.ref(
            "somconnexio.100MinSenseDades_product_template"
        ).product_variant_id
        lead_line_vals = {
            'name': '666666666',
            'product_id': product_mobile.id,
            'mobile_isp_info': mobile_isp_info.id,
        }
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': None,
                'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
            }]
        )
        self.assertRaisesRegex(
            ValidationError,
            "Error in {}: The subscription request related must be validated.".format(crm_lead.lead_line_id),  # noqa
            crm_lead.action_set_remesa
        )

    def test_crm_lead_action_set_remesa_raise_error_with_invalid_bank(self):
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'new',
        })
        product_mobile = self.env.ref(
            "somconnexio.100MinSenseDades_product_template"
        ).product_variant_id
        lead_line_vals = {
            'name': '666666666',
            'product_id': product_mobile.id,
            'mobile_isp_info': mobile_isp_info.id,
        }
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'iban': 'ES6099991500051234567891',
                'lead_line_ids': [(0, 0, lead_line_vals)],
            }]
        )
        self.assertRaisesRegex(
            ValidationError,
            "Error in {}: Invalid bank.".format(crm_lead.lead_line_id),
            crm_lead.action_set_remesa
        )

    def test_crm_lead_action_set_remesa_raise_error_with_existent_phone_number(self):
        product_mobile = self.env.ref(
            "somconnexio.100MinSenseDades_product_template"
        ).product_variant_id
        previous_provider = self.ref("somconnexio.previousprovider1")
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'portability',
            'phone_number': '663322234',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider,
        })
        lead_line_vals = {
            'name': '663322234',
            'product_id': product_mobile.id,
            'mobile_isp_info': mobile_isp_info.id,
        }
        self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
                'stage_id': self.env.ref("crm.stage_lead4").id,
            }]
        )
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
            }]
        )

        self.assertRaisesRegex(
            ValidationError,
            "Error in {}: Contract or validated CRMLead with the same phone already exists.".format(crm_lead.lead_line_id),  # noqa
            crm_lead.action_set_remesa
        )

    def test_crm_lead_action_set_remesa_raise_error_with_duplicate_phone_number_in_new_line(self):  # noqa
        product_mobile = self.env.ref(
            "somconnexio.100MinSenseDades_product_template"
        ).product_variant_id
        previous_provider = self.ref("somconnexio.previousprovider1")
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'portability',
            'phone_number': '663322234',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider,
        })
        lead_line_vals = {
            'name': '663322234',
            'product_id': product_mobile.id,
            'mobile_isp_info': mobile_isp_info.id,
        }
        crm_leads = self.env['crm.lead'].create(
            [
                {
                    'name': 'Test Lead',
                    'partner_id': self.partner_id.id,
                    'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                    'lead_line_ids': [(0, 0, lead_line_vals)],
                    'stage_id': self.env.ref("crm.stage_lead1").id,
                },
                {
                    'name': 'Test Lead',
                    'partner_id': self.partner_id.id,
                    'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                    'lead_line_ids': [(0, 0, lead_line_vals)],
                    'stage_id': self.env.ref("crm.stage_lead1").id,
                }
            ]
        )
        self.assertRaisesRegex(
            ValidationError,
            "Error in {}: Duplicated phone number in CRMLead petitions.".format(crm_leads[0].lead_line_id),  # noqa
            crm_leads.action_set_remesa,
        )

    def test_crm_lead_action_set_remesa_dont_raise_error_with_existent_phone_number_if_skip_true(self):  # noqa
        product_mobile = self.env.ref(
            "somconnexio.100MinSenseDades_product_template"
        ).product_variant_id
        previous_provider = self.ref("somconnexio.previousprovider1")
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'portability',
            'phone_number': '663322234',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider,
        })
        lead_line_vals = {
            'name': '663322234',
            'product_id': product_mobile.id,
            'mobile_isp_info': mobile_isp_info.id,
        }
        self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
                'stage_id': self.env.ref("crm.stage_lead4").id,
            }]
        )
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
                'skip_duplicated_phone_validation': True
            }]
        )

        self.assertNotEquals(crm_lead.stage_id, self.browse_ref('crm.stage_lead3'))
        crm_lead.action_set_remesa()
        self.assertEquals(crm_lead.stage_id, self.browse_ref('crm.stage_lead3'))

    def test_mobile_phone_number_portability_format_validation(self):
        product_mobile = self.env.ref(
            "somconnexio.100MinSenseDades_product_template"
        ).product_variant_id
        previous_provider = self.ref("somconnexio.previousprovider1")
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'portability',
            'phone_number': '497453838',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider,
        })
        lead_line_vals = {
            'name': '497453838',
            'product_id': product_mobile.id,
            'mobile_isp_info': mobile_isp_info.id,
        }
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
            }]
        )

        self.assertRaisesRegex(
            ValidationError,
            'Mobile phone number has to be a 9 digit number starting with 6 or 7',
            crm_lead.action_set_remesa
        )

    def test_broadband_phone_number_portability_format_validation(self):
        product_broadband = self.env.ref(
            "somconnexio.ADSL20MB100MinFixMobile_product_template"
        ).product_variant_id
        previous_provider = self.ref("somconnexio.previousprovider3")
        broadband_isp_info = self.env['broadband.isp.info'].create({
            'type': 'portability',
            'phone_number': '497453838',
            'previous_service': 'adsl',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider,
        })
        lead_line_vals = {
            'name': '497453838',
            'product_id': product_broadband.id,
            'broadband_isp_info': broadband_isp_info.id,
        }
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner_id.id,
                'iban': self.partner_id.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
            }]
        )

        self.assertRaisesRegex(
            ValidationError,
            'Landline phone number has to be a 9 digit number starting with 8 or 9',
            crm_lead.action_set_remesa
        )
