from datetime import datetime
from ..sc_test_case import SCTestCase


class TestContractOneShotRequestWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.start_date = datetime.strftime(datetime.today(), "%Y-%m-%d")
        self.masmovil_mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'icc': '123',
        })
        self.partner = self.browse_ref('base.partner_demo')
        partner_id = self.partner.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        vals_contract = {
            'name': 'Test Contract One Shot Request',
            'partner_id': partner_id,
            'service_partner_id': service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_mobile"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mobile_contract_service_info_id': (
                self.masmovil_mobile_contract_service_info.id
            ),
            'bank_id': self.partner.bank_ids.id
        }
        self.contract = self.env['contract.contract'].create(vals_contract)
        self.user_admin = self.browse_ref('base.user_admin')

    def test_wizard_one_shot_request_sim(self):
        product = self.browse_ref('somconnexio.EnviamentSIM')

        self.assertEqual(len(self.contract.contract_line_ids), 0)

        wizard = self.env['contract.one.shot.request.wizard'].with_context(
            active_id=self.contract.id
        ).sudo(
            self.user_admin
        ).create({
            'start_date': self.start_date,
            'one_shot_product_id': product.id,
            'summary': '',
        })
        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)],
        )
        self.assertEquals(len(partner_activities_after) -
                          len(partner_activities_before), 1)
        created_activity = partner_activities_after[-1]
        self.assertEquals(created_activity.user_id, self.user_admin)
        self.assertEquals(
            created_activity.activity_type_id,
            self.browse_ref('somconnexio.mail_activity_type_sim_change')
        )
        self.assertEquals(created_activity.done, wizard.done)
        self.assertEquals(created_activity.summary, wizard.summary)
        self.assertEqual(len(self.contract.contract_line_ids), 1)

    def test_wizard_one_shot_request_additional_sms(self):
        self.assertEqual(len(self.contract.contract_line_ids), 0)
        product = self.browse_ref('somconnexio.SMSMassius500SMS')
        wizard = self.env['contract.one.shot.request.wizard'].with_context(
            active_id=self.contract.id
        ).sudo(
            self.user_admin
        ).create({
            'start_date': self.start_date,
            'one_shot_product_id': product.id,
            'summary': '',
        })
        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)],
        )
        self.assertEquals(len(partner_activities_after) -
                          len(partner_activities_before), 1)
        created_activity = partner_activities_after[-1]
        self.assertEquals(created_activity.user_id, self.user_admin)
        self.assertEquals(
            created_activity.activity_type_id,
            self.browse_ref('somconnexio.mail_activity_type_one_shot')
        )
        self.assertEquals(created_activity.done, wizard.done)
        self.assertEquals(created_activity.summary, wizard.summary)
        self.assertEqual(len(self.contract.contract_line_ids), 1)

    def test_wizard_one_shot_request_additional_data(self):
        self.assertEqual(len(self.contract.contract_line_ids), 0)
        product = self.browse_ref('somconnexio.DadesAddicionals500MB')
        wizard = self.env['contract.one.shot.request.wizard'].with_context(
            active_id=self.contract.id
        ).sudo(
            self.user_admin
        ).create({
            'start_date': self.start_date,
            'one_shot_product_id': product.id,
            'summary': 'test',
        })
        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)],
        )
        self.assertEquals(len(partner_activities_after) -
                          len(partner_activities_before), 1)
        created_activity = partner_activities_after[-1]
        self.assertEquals(created_activity.user_id, self.user_admin)
        self.assertEquals(
            created_activity.activity_type_id,
            self.browse_ref('somconnexio.mail_activity_type_one_shot')
        )
        self.assertEquals(created_activity.done, wizard.done)
        self.assertEquals(created_activity.summary, product.showed_name)
        self.assertEqual(len(self.contract.contract_line_ids), 1)

    def test_wizard_one_shot_request_send_return_router(self):
        self.partner = self.browse_ref('base.partner_demo')
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        service_partner = self.env['res.partner'].create({
            'parent_id': self.partner.id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        values_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': self.partner.id,
            'service_partner_id': service_partner.id,
            'invoice_partner_id': self.partner.id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_vodafone"
            ),
            'vodafone_fiber_service_contract_info_id': (
                self.vodafone_fiber_contract_service_info.id
            ),
            'bank_id': self.partner.bank_ids.id
        }
        self.contract = self.env['contract.contract'].create(values_contract)

        self.assertEqual(len(self.contract.contract_line_ids), 0)
        product = self.browse_ref('somconnexio.EnviamentRouter')
        wizard = self.env['contract.one.shot.request.wizard'].with_context(
            active_id=self.contract.id
        ).sudo(
            self.user_admin
        ).create({
            'start_date': self.start_date,
            'one_shot_product_id': product.id,
            'summary': 'test',
        })
        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)],
        )
        self.assertEquals(len(partner_activities_after) -
                          len(partner_activities_before), 1)
        created_activity = partner_activities_after[-1]
        self.assertEquals(created_activity.user_id, self.user_admin)
        self.assertEquals(
            created_activity.activity_type_id,
            self.browse_ref('somconnexio.mail_activity_type_router_send_or_return')
        )
        self.assertEquals(created_activity.done, wizard.done)
        self.assertEquals(created_activity.summary, wizard.summary)
        self.assertEqual(len(self.contract.contract_line_ids), 1)
