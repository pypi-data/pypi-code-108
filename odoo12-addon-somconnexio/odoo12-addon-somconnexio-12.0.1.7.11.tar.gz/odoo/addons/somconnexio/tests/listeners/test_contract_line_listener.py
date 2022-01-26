from mock import patch

from odoo import fields
from odoo.addons.component.tests.common import ComponentMixin
from odoo.tests.common import SavepointCase


class TestContractLineListener(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestContractLineListener, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self, *args, **kwargs):
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

        self.ContractLine = self.env['contract.line']
        self.ba_service = self.browse_ref('somconnexio.Fibra600Mb')
        self.mobile_service = self.browse_ref('somconnexio.SenseMinutsSenseDades')
        self.ba_one_shot = self.browse_ref('somconnexio.AltaParellExistent')
        self.mobile_one_shot = self.browse_ref('somconnexio.DadesAddicionals500MB')
        self.international_mins = self.browse_ref('somconnexio.Internacional100Min')
        self.ip_fixa = self.browse_ref('somconnexio.IPv4Fixa')

        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '999990999',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'icc': '123'
        })
        self.partner = self.browse_ref('base.partner_demo')
        partner_id = self.partner.id
        self.service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        self.ba_contract = self.env['contract.contract'].create({
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': partner_id,
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
        })
        self.mobile_contract = self.env['contract.contract'].create({
            'name': 'Test Contract Mobile',
            'partner_id': partner_id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_mobile"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mobile_contract_service_info_id': (
                self.mobile_contract_service_info.id
            ),
            'bank_id': self.partner.bank_ids.id
        })

    def test_create_line_with_mobile_service(self):
        cl = self.ContractLine.create({
            "name": self.mobile_service.name,
            "contract_id": self.mobile_contract.id,
            "product_id": self.mobile_service.id,
            "date_start": fields.Date.today()
        })

        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env['queue.job'].search(jobs_domain)

        self.assertEquals(1, len(queued_jobs))
        self.assertEquals(
            queued_jobs.args,
            [
                self.mobile_contract.id,
                cl
            ]
        )

    def test_create_line_with_ba_service(self):
        cl = self.ContractLine.create({
            "name": self.ba_service.name,
            "contract_id": self.ba_contract.id,
            "product_id": self.ba_service.id,
            "date_start": fields.Date.today()
        })

        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env['queue.job'].search(jobs_domain)

        self.assertEquals(1, len(queued_jobs))
        self.assertEquals(
            queued_jobs.args,
            [
                self.ba_contract.id,
                cl
            ]
        )

    def test_create_line_with_mobile_one_shot(self):
        self.ContractLine.create({
            "name": self.mobile_one_shot.name,
            "contract_id": self.mobile_contract.id,
            "product_id": self.mobile_one_shot.id,
            "date_start": fields.Date.today()
        })

        jobs_domain = [
            ("method_name", "=", "add_one_shot"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env['queue.job'].search(jobs_domain)

        self.assertEquals(1, len(queued_jobs))
        self.assertEquals(
            queued_jobs.args,
            [
                self.mobile_contract.id,
                self.mobile_one_shot.default_code,
            ]
        )

    def test_create_line_with_ba_one_shot(self):
        self.ContractLine.create({
            "name": self.ba_one_shot.name,
            "contract_id": self.ba_contract.id,
            "product_id": self.ba_one_shot.id,
            "date_start": fields.Date.today()
        })

        jobs_domain = [
            ("method_name", "=", "add_one_shot"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env['queue.job'].search(jobs_domain)

        self.assertEquals(1, len(queued_jobs))
        self.assertEquals(
            queued_jobs.args,
            [
                self.ba_contract.id,
                self.ba_one_shot.default_code
            ]
        )

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_create_line_with_mobile_additional_service(self, message_post_mock):
        cl = self.ContractLine.create({
            "name": self.international_mins.name,
            "contract_id": self.mobile_contract.id,
            "product_id": self.international_mins.id,
            "date_start": fields.Date.today()
        })

        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env['queue.job'].search(jobs_domain)

        self.assertEquals(1, len(queued_jobs))
        self.assertEquals(
            queued_jobs.args,
            [
                self.mobile_contract.id,
                cl
            ]
        )
        message_post_mock.assert_called_with(
            body="Added product {} with start date {}".format(
                self.international_mins.showed_name,
                fields.Date.today()
            )
        )

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_create_line_with_ba_additional_service(self, message_post_mock):
        cl = self.ContractLine.create({
            "name": self.ip_fixa.name,
            "contract_id": self.ba_contract.id,
            "product_id": self.ip_fixa.id,
            "date_start": fields.Date.today()
        })

        jobs_domain = [
            ("method_name", "=", "add_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env['queue.job'].search(jobs_domain)

        self.assertEquals(1, len(queued_jobs))
        self.assertEquals(
            queued_jobs.args,
            [
                self.ba_contract.id,
                cl
            ]
        )
        message_post_mock.assert_called_with(
            body="Added product {} with start date {}".format(
                self.ip_fixa.showed_name,
                fields.Date.today()
            )
        )

    @patch('odoo.addons.mail.models.mail_thread.MailThread.message_post')
    def test_terminate_line_enqueue_terminate_service(self, message_post_mock):
        cl = self.ContractLine.create({
            "name": self.ip_fixa.name,
            "contract_id": self.ba_contract.id,
            "product_id": self.ip_fixa.id,
            "date_start": fields.Date.today()
        })
        cl.write({
            "date_end": fields.Date.today()
        })

        jobs_domain = [
            ("method_name", "=", "terminate_service"),
            ("model_name", "=", "contract.contract"),
        ]
        queued_jobs = self.env['queue.job'].search(jobs_domain)

        self.assertEquals(1, len(queued_jobs))
        self.assertEquals(
            queued_jobs.args,
            [
                self.ba_contract.id,
                cl
            ]
        )
        message_post_mock.assert_called_with(
            body="Updated product {} with end date {}".format(
                self.ip_fixa.showed_name,
                fields.Date.today()
            )
        )
