from odoo import _
from odoo.exceptions import ValidationError
from ..sc_test_case import SCTestCase


class TestCRMLeadsRemesaWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.remesa_stage = self.browse_ref('crm.stage_lead3')
        self.partner = self.browse_ref('somconnexio.res_partner_2_demo')
        crm_lead = self.env['crm.lead'].create(
            {
                'name': 'NewCRMLead',
                'partner_id': self.partner.id,
                'iban': self.partner.bank_ids[0].sanitized_acc_number,
            }
        )
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'new',
        })
        self.product = self.env.ref(
            "somconnexio.100MinSenseDades_product_template"
        ).product_variant_id
        self.crm_lead_line_args = {
            'name': 'New LeadLine',
            'product_id': self.product.id,
            'mobile_isp_info': mobile_isp_info.id,
            'broadband_isp_info': None,
            'lead_id': crm_lead.id
        }
        self.crm_lead_line = self.env['crm.lead.line'].create(
            [self.crm_lead_line_args]
        )

    def test_wizard_ok(self):
        wizard = self.env['crm.lead.lines.remesa.wizard'].with_context(
            active_ids=[self.crm_lead_line.id]
        ).create({})
        wizard.button_remesa()
        self.assertEquals(
            self.crm_lead_line.lead_id.stage_id,
            self.remesa_stage
        )

    def test_validation_error(self):
        self.crm_lead_line.lead_id.partner_id = None
        self.crm_lead_line.lead_id.subscription_request_id = self.browse_ref(
            "somconnexio.sc_subscription_request_1_demo"
        )
        with self.assertRaises(ValidationError):
            self.env['crm.lead.lines.remesa.wizard'].with_context(
                active_ids=[self.crm_lead_line.id]
            ).create({})

    def test_skip_phone_validation(self):
        previous_provider = self.ref("somconnexio.previousprovider1")
        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'portability',
            'phone_number': '663322234',
            'previous_contract_type': 'contract',
            'previous_provider': previous_provider,
        })
        lead_line_vals = {
            'name': '663322234',
            'product_id': self.product.id,
            'mobile_isp_info': mobile_isp_info.id,
        }
        self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner.id,
                'iban': self.partner.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
                'stage_id': self.env.ref("crm.stage_lead4").id,
            }]
        )
        crm_lead = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': self.partner.id,
                'iban': self.partner.bank_ids[0].sanitized_acc_number,
                'lead_line_ids': [(0, 0, lead_line_vals)],
            }]
        )

        crm_lead_line_id = crm_lead.lead_line_ids[0].id
        wizard = self.env['crm.lead.lines.remesa.wizard'].with_context(
            active_ids=[crm_lead_line_id]
        ).create({})

        self.assertEqual(
            wizard.errors,
            _("The next CRMLeadLines have a phone number that already exists in another contract/CRMLead: {}").format(  # noqa
                crm_lead_line_id
            )
        )
        wizard.button_remesa()
        self.assertEquals(
            crm_lead.stage_id,
            self.remesa_stage
        )
