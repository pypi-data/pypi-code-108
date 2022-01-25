import odoo
import json
from odoo.exceptions import UserError
from odoo.addons.easy_my_coop_api.tests.common import BaseEMCRestCase
from ...services.contract_iban_change_process import ContractIbanChangeProcess
HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCaseAdmin(BaseEMCRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        # Skip parent class in super to avoid recreating api key
        super(BaseEMCRestCase, cls).setUpClass(*args, **kwargs)


class TestContractIBANChangeService(BaseEMCRestCaseAdmin):

    def setUp(self, *args, **kwargs):
        super().setUp()
        self.Contract = self.env['contract.contract']
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.partner = self.browse_ref('base.partner_demo')
        self.partner.ref = "1234test"
        self.partner_ref = self.partner.ref
        self.partner.customer = True
        partner_id = self.partner.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        self.bank_b = self.env['res.partner.bank'].create({
            'acc_number': 'ES1720852066623456789011',
            'partner_id': partner_id
        })
        self.iban = 'ES6700751951971875361545'
        self.bank_new = self.env['res.partner.bank'].create({
            'acc_number': self.iban,
            'partner_id': partner_id
        })
        self.banking_mandate = self.env['account.banking.mandate'].search([
            ('partner_bank_id', '=', self.bank_b.id),
        ])
        self.banking_mandate_new = self.env['account.banking.mandate'].search([
            ('partner_bank_id', '=', self.bank_new.id),
        ])
        vals_contract = {
            'code': 'contract1test',
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': service_partner.id,
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
            'mandate_id': self.banking_mandate.id
        }
        self.contract = self.env['contract.contract'].create(vals_contract)
        vals_contract_same_partner = vals_contract.copy()
        vals_contract_same_partner.update({
            'name': 'Test Contract Broadband B',
            'code': 'contract2test',
        })
        self.contract_same_partner = self.env['contract.contract'].with_context(
            tracking_disable=True
        ).create(
            vals_contract_same_partner
        )

    def http_public_post(self, url, data, headers=None):
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)
        return self.session.post(url, json=data)

    def test_route_right_run_wizard_all_contracts(self):
        url = "/public-api/contract-iban-change"
        data = {
            "partner_id": self.partner_ref,
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        process.run_from_api(**data)
        self.assertEquals(self.contract.mandate_id, self.banking_mandate_new)
        self.assertEquals(
            self.contract_same_partner.mandate_id, self.banking_mandate_new
        )

    def test_route_right_run_wizard_one_contract(self):
        url = "/public-api/contract-iban-change"
        data = {
            "partner_id": self.partner_ref,
            "iban": self.iban,
            "contracts": "{}".format(self.contract.code)
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        process.run_from_api(**data)
        self.assertEquals(self.contract.mandate_id, self.banking_mandate_new)
        self.assertEquals(self.contract_same_partner.mandate_id, self.banking_mandate)

    def test_route_right_run_wizard_many_contracts(self):
        url = "/public-api/contract-iban-change"
        data = {
            "partner_id": self.partner_ref,
            "iban": self.iban,
            "contracts": "{};{}".format(
                self.contract.code, self.contract_same_partner.code
            )
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        process.run_from_api(**data)
        self.assertEquals(self.contract.mandate_id, self.banking_mandate_new)
        self.assertEquals(
            self.contract_same_partner.mandate_id, self.banking_mandate_new
        )

    def test_route_right_new_iban(self):
        url = "/public-api/contract-iban-change"
        missing_iban = 'ES1000492352082414205416'
        data = {
            "partner_id": self.partner_ref,
            "iban": missing_iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        process.run_from_api(**data)
        acc_number = self.contract.mandate_id.partner_bank_id.acc_number
        self.assertEquals(
            acc_number.replace(' ', '').upper(),
            missing_iban
        )
        acc_number = self.contract_same_partner.mandate_id.partner_bank_id.acc_number
        self.assertEquals(
            acc_number.replace(' ', '').upper(),
            missing_iban
        )

    def test_route_bad_iban(self):
        url = "/public-api/contract-iban-change"
        data = {
            "partner_id": self.partner_ref,
            "iban": 'XXX',
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_bad_unexpected_iban_error(self):
        self.partner.customer = False
        url = "/public-api/contract-iban-change"
        missing_iban = 'ES1000492352082414205416'
        data = {
            "partner_id": self.partner_ref,
            "iban": missing_iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_bad_contract(self):
        url = "/public-api/contract-iban-change"
        data = {
            "partner_id": self.partner_ref,
            "iban": self.iban,
            "contracts": "{};XXX".format(self.contract)
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_missing_iban(self):
        url = "/public-api/contract-iban-change"
        data = {
            "partner_id": self.partner_ref,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)

    def test_route_missing_partner_id(self):
        url = "/public-api/contract-iban-change"
        data = {
            "iban": self.iban,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractIbanChangeProcess(self.env)
        self.assertRaises(UserError, process.run_from_api, **data)
