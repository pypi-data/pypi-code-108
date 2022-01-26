import odoo
import json
from odoo.exceptions import UserError
from odoo.addons.easy_my_coop_api.tests.common import BaseEMCRestCase
from ...services.contract_one_shot_process import ContractOneShotProcess
HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCaseAdmin(BaseEMCRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        # Skip parent class in super to avoid recreating api key
        super(BaseEMCRestCase, cls).setUpClass(*args, **kwargs)


class TestContractOneShotService(BaseEMCRestCaseAdmin):

    def setUp(self, *args, **kwargs):
        super().setUp()
        self.Contract = self.env['contract.contract']

        self.phone = "654321123"
        self.mobile_one_shot = self.browse_ref('somconnexio.DadesAddicionals1GB')
        self.data = {
            "product_code": self.mobile_one_shot.default_code,
            "phone_number": self.phone,
        }

        self.mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': self.phone,
            'icc': '123'
        })
        self.partner = self.browse_ref('base.partner_demo')
        self.mobile_contract = self.Contract.create({
            'name': 'Test Contract Mobile',
            'partner_id': self.partner.id,
            'service_partner_id': self.partner.id,
            'invoice_partner_id': self.partner.id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_mobile"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mobile_contract_service_info_id': (
                self.mobile_contract_service_info.id
            ),
        })
        self.url = "/public-api/add-one-shot"

    def http_public_post(self, url, data, headers=None):
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)
        return self.session.post(url, json=data)

    def test_route_right_run_wizard(self):
        response = self.http_public_post(self.url, data=self.data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractOneShotProcess(self.env)
        process.run_from_api(**self.data)
        partner_activities = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)],
        )
        created_activity = partner_activities[-1]

        self.assertEqual(len(self.mobile_contract.contract_line_ids), 1)
        self.assertEqual(self.mobile_contract.contract_line_ids[0].product_id,
                         self.mobile_one_shot)
        self.assertEquals(created_activity.summary, 'Abonament addicional de {}'.format(
            self.mobile_one_shot.showed_name))

    def test_route_bad_phone(self):
        wrong_phone = "8383838"
        self.data.update({"phone_number": wrong_phone})

        response = self.http_public_post(self.url, data=self.data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractOneShotProcess(self.env)
        self.assertRaisesRegex(
            UserError,
            "Mobile contract not found with phone: {}".format(wrong_phone),
            process.run_from_api, **self.data
        )

    def test_route_bad_product(self):
        wrong_product = "FAKE_DEFAULT_CODE"
        self.data.update({"product_code": wrong_product})

        response = self.http_public_post(self.url, data=self.data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractOneShotProcess(self.env)
        self.assertRaisesRegex(
            UserError,
            "Mobile additional bond product not found with code: {}".format(
                wrong_product),
            process.run_from_api, **self.data
        )
