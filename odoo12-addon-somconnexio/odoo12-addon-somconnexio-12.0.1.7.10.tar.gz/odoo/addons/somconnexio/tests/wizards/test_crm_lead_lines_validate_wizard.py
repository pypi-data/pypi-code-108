from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class TestCRMLeadLinesValidateWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.crm_lead = self.env['crm.lead'].create(
            [{'name': 'Test Lead'}]
        )
        self.partner_id = self.browse_ref('somconnexio.res_partner_2_demo')

        crm_lead_line_args = {
            'name': 'Test Crm Lead Line',
            'product_id': None,
            'mobile_isp_info': None,
            'broadband_isp_info': None,
        }

        mobile_isp_info = self.env['mobile.isp.info'].create({
            'type': 'new',
        })
        product_mobile = self.env['product.product'].search(
            [('default_code', '=', 'SE_SC_REC_MOBILE_T_0_2048')]
        )

        crm_lead_line_args_mbl = crm_lead_line_args.copy()
        crm_lead_line_args_mbl.update({
            'mobile_isp_info': mobile_isp_info.id,
            'product_id': product_mobile.id
        })
        self.mobile_crm_lead_line = self.env['crm.lead.line'].create(
            [crm_lead_line_args_mbl]
        )

        broadband_isp_info = self.env['broadband.isp.info'].create({
            'type': 'new'
        })

        product_BA = self.env['product.product'].search(
            [('default_code', '=', 'SE_SC_REC_BA_ADSL_100')]
        )

        crm_lead_line_args_BA = crm_lead_line_args.copy()
        crm_lead_line_args_BA.update({
            'broadband_isp_info': broadband_isp_info.id,
            'product_id': product_BA.id
        })

        self.BA_crm_lead_line = self.env['crm.lead.line'].create(
            [crm_lead_line_args_BA]
        )

    def test_wizard_validate_mobile_line_ok(self):

        self.crm_lead.write(
            {
                'lead_line_ids': [(4, self.mobile_crm_lead_line.id, False)],
                'stage_id': self.browse_ref('crm.stage_lead3').id,
            }
        )

        wizard = self.env['crm.lead.lines.validate.wizard'].with_context(
            active_ids=[self.mobile_crm_lead_line.id]
        ).create({
            'crm_lead_line_ids': [(4, self.mobile_crm_lead_line.id, False)]
        })

        self.assertNotEqual(self.crm_lead.stage_id, self.browse_ref('crm.stage_lead4'))
        wizard.button_validate()
        self.assertEquals(self.crm_lead.stage_id, self.browse_ref('crm.stage_lead4'))

    def test_wizard_validate_BA_line_ok(self):

        self.crm_lead.write(
            {
                'lead_line_ids': [(4, self.BA_crm_lead_line.id, False)],
                'stage_id': self.browse_ref('crm.stage_lead3').id,
            }
        )

        wizard = self.env['crm.lead.lines.validate.wizard'].with_context(
            active_ids=[self.BA_crm_lead_line.id]
        ).create({
            'crm_lead_line_ids': [(4, self.BA_crm_lead_line.id, False)]
        })
        self.assertNotEqual(self.crm_lead.stage_id, self.browse_ref('crm.stage_lead4'))
        wizard.button_validate()
        self.assertEquals(self.crm_lead.stage_id, self.browse_ref('crm.stage_lead4'))

    def test_wizard_validate_CRMLead_with_multiple_CRM_lines_ko(self):

        crm_lines_list = [self.BA_crm_lead_line.id, self.mobile_crm_lead_line.id]

        self.crm_lead.write({
            'lead_line_ids': [(6, False, crm_lines_list)]
        })

        wizard = self.env['crm.lead.lines.validate.wizard'].with_context(
            active_ids=[self.BA_crm_lead_line.id]
        ).create({
            'crm_lead_line_ids': [(4, self.BA_crm_lead_line.id, False)]
        })
        self.assertRaises(
            ValidationError,
            wizard.button_validate
        )
