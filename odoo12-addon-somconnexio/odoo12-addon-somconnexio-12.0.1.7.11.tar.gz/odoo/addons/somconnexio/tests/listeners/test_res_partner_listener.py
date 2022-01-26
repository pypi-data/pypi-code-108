from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import SavepointCase


class TestResPartnerListener(SavepointCase, ComponentMixin):

    @classmethod
    def setUpClass(cls):
        super(TestResPartnerListener, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self):
        # resolve an inheritance issue (SavepointCase does not call super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)
        self.partner = self.browse_ref('somconnexio.res_partner_2_demo')
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.contract_fiber_args = {
            'name': 'Contract w/service technology to fiber',
            'service_technology_id': self.ref(
                'somconnexio.service_technology_fiber'
            ),
            'service_supplier_id': self.ref(
                'somconnexio.service_supplier_vodafone'
            ),
            'vodafone_fiber_service_contract_info_id': (
                self.vodafone_fiber_contract_service_info.id
            ),
            'partner_id': self.partner.id,
            'service_partner_id': self.partner.id,
            'invoice_partner_id': self.partner.id,
            'bank_id': self.partner.bank_ids[0].id,
        }
        self.env['contract.contract'].create(self.contract_fiber_args)

    def test_res_partner_listener_edit_address_field(self):
        queue_jobs_before = self.env['queue.job'].search([])
        self.partner.write({
            "street": "street test"
        })
        queue_jobs_after = self.env['queue.job'].search([])
        self.assertEquals(2, len(queue_jobs_after - queue_jobs_before))

    def test_res_partner_listener_edit_not_address_field(self):
        queue_jobs_before = self.env['queue.job'].search([])
        self.partner.write({
            "name": "test"
        })
        queue_jobs_after = self.env['queue.job'].search([])
        self.assertEquals(0, len(queue_jobs_after - queue_jobs_before))

    def test_res_partner_listener_edit_address_and_not_address_field(self): # noqa
        queue_jobs_before = self.env['queue.job'].search([])
        self.partner.write({
            "name": "test",
            "street": "street test"
        })
        queue_jobs_after = self.env['queue.job'].search([])
        self.assertEquals(2, len(queue_jobs_after - queue_jobs_before))
