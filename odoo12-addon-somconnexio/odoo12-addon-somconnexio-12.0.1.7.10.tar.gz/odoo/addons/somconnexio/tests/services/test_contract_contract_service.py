import json
import odoo
from faker import Faker
from odoo.addons.easy_my_coop_api.tests.common import BaseEMCRestCase
from datetime import date, timedelta, datetime
from mock import patch
from ...services.contract_contract_process import ContractContractProcess
from odoo.exceptions import UserError
HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCaseAdmin(BaseEMCRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        # Skip parent class in super to avoid recreating api key
        super(BaseEMCRestCase, cls).setUpClass(*args, **kwargs)
        cls.AuthApiKey = cls.env["auth.api.key"]
        admin = cls.env.ref("base.user_admin")
        cls.api_key_test = cls.AuthApiKey.create(
            {"name": "test-key", "key": "api-key", "user_id": admin.id}
        )


@patch("pyopencell.resources.subscription.Subscription.get")
@patch('odoo.addons.somconnexio.models.contract.CRMAccountHierarchyFromContractCreateService')  # noqa
class TestContractController(BaseEMCRestCaseAdmin):

    def setUp(self):
        super().setUp()
        self.router_product = self.env['product.product'].search(
            [
                ("default_code", "=", "HG8245Q2"),
            ]
        )
        partner = self.browse_ref('somconnexio.res_partner_2_demo')

        self.partner_ref = partner.ref

        self.iban = partner.bank_ids[0].acc_number

        self.email = partner.email

        fake = Faker('es-ES')

        self.mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': partner.bank_ids[0].id,
            'state': 'valid',
            'partner_id': partner.id,
            'signature_date': fake.date_time_this_month()
        })

        self.service_address = {
            'street': fake.street_address() + " " + fake.secondary_address(),
            'zip_code': fake.postcode(),
            'city': fake.city(),
            'state': self.browse_ref('base.state_es_m').code,
            'country': self.browse_ref('base.es').code,
        }
        self.ticket_number = "1234"

    def http_public_post(self, url, data, headers=None):
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)
        return self.session.post(url, json=data)

    def test_route_right_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(
            contract.name,
            data['mobile_contract_service_info']['phone_number']
        )
        self.assertEquals(
            contract.partner_id,
            self.browse_ref('somconnexio.res_partner_2_demo')
        )
        self.assertEquals(
            contract.journal_id,
            self.browse_ref('somconnexio.consumption_invoices_journal')
        )
        self.assertEquals(
            contract.invoice_partner_id,
            self.browse_ref('somconnexio.res_partner_2_demo')
        )
        self.assertEquals(
            contract.service_technology_id,
            self.browse_ref('somconnexio.service_technology_mobile')
        )
        self.assertEquals(
            contract.service_supplier_id,
            self.browse_ref('somconnexio.service_supplier_masmovil')
        )
        self.assertTrue(
            contract.mobile_contract_service_info_id
        )
        self.assertEquals(
            contract.mobile_contract_service_info_id.icc,
            data['mobile_contract_service_info']['icc']
        )
        self.assertEquals(
            contract.mobile_contract_service_info_id.phone_number,
            data['mobile_contract_service_info']['phone_number']
        )
        self.assertEquals(
            contract.mandate_id,
            self.mandate
        )
        self.assertEquals(
            contract.ticket_number,
            self.ticket_number
        )

    def test_route_bad_partner_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": "666",
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": "IBAN",
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    def test_route_bad_tech_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'XXXX',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_supplier_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "XXXX",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_fiber_signal_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Fiber',
            "service_supplier": "MásMóvil",
            "mm_fiber_contract_service_info": {
                "phone_number": "654123456",
                'mm_id': "123"
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_combination_create(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Fiber',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    def test_route_right_contract_lines(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "date_start": "2020-01-01 00:00:00"
                },
                {
                    "product_code": (
                        self.browse_ref('somconnexio.EnviamentSIM').default_code
                    ),
                    "date_start": "2020-01-01 00:00:00"
                }
            ],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(
            contract.name,
            data['mobile_contract_service_info']['phone_number']
        )
        self.assertEquals(
            contract.partner_id,
            self.browse_ref('somconnexio.res_partner_2_demo')
        )
        self.assertEquals(
            contract.invoice_partner_id,
            self.browse_ref('somconnexio.res_partner_2_demo')
        )
        self.assertEquals(
            contract.service_technology_id,
            self.browse_ref('somconnexio.service_technology_mobile')
        )
        self.assertEquals(
            contract.service_supplier_id,
            self.browse_ref('somconnexio.service_supplier_masmovil')
        )
        self.assertEquals(
            contract.ticket_number,
            self.ticket_number
        )
        self.assertIn(
            self.browse_ref('somconnexio.150Min1GB'), [
                c.product_id
                for c in contract.contract_line_ids
            ]
        )
        self.assertIn(
            self.browse_ref('somconnexio.EnviamentSIM'), [
                c.product_id
                for c in contract.contract_line_ids
            ]
        )
        self.assertEquals(
            contract.current_tariff_product,
            self.env.ref('somconnexio.150Min1GB')
        )
        self.assertEquals(
            [date(2020, 1, 1), date(2020, 1, 1)],
            contract.contract_line_ids.mapped('date_start'),
        )
        contract.contract_line_ids[0].date_start = date(2020, 1, 2)
        self.assertEquals(contract.date_start, date(2020, 1, 1))

    def test_route_right_contract_line(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_line": {
                "product_code": (
                    self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                "date_start": "2020-01-01 00:00:00"
                },
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertIn(
            self.browse_ref('somconnexio.150Min1GB'), [
                c.product_id
                for c in contract.contract_line_ids
            ]
        )
        self.assertEquals(
            [date(2020, 1, 1)],
            contract.contract_line_ids.mapped('date_start'),
        )

    def test_route_contract_without_active_tariff(self, *args):
        url = "/public-api/contract"
        tomorrow = date.today() + timedelta(days=1)
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "date_start": tomorrow.strftime("%Y-%m-%d %H:%M:%S"),
                },
                {
                    "product_code": (
                        self.browse_ref('somconnexio.EnviamentSIM').default_code
                    ),
                    "date_start": "2020-01-01 00:00:00"
                }
            ],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertFalse(contract.current_tariff_contract_line)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_call_both_contract_lines(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_line": {
                "product_code": (
                    self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                "date_start": "2020-01-01 00:00:00"
                },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_date_start(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "date_start": "6666-66-66 66:66:66"
                }
            ],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_product_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "date_start": "2020-01-01 00:00:00"
                },
                {
                    "product_code": "SC_0",
                    "date_start": "2020-01-01 00:00:00"
                }
            ],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_format_product(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "date_start": "2020-01-01 00:00:00"
                },
                {
                    "product_code": 666,
                    "date_start": "2020-01-01 00:00:00"
                }
            ],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_mobile_missing_icc(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_mobile_missing_phone_number(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    def test_route_right_adsl(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'ADSL',
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(
            contract.name,
            data['adsl_contract_service_info']['phone_number']
        )

        self.assertTrue(contract.adsl_service_contract_info_id)
        contract_service_info = contract.adsl_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '654123456')
        self.assertEquals(contract_service_info.administrative_number, '123')
        self.assertEquals(
            contract_service_info.router_lot_id.product_id.id,
            self.router_product.id
        )
        self.assertEquals(
            contract_service_info.router_lot_id.name,
            '4637'
        )
        self.assertEquals(
            contract_service_info.router_lot_id.router_mac_address,
            'AA:BB:CC:22:33:11'
        )
        self.assertEquals(
            contract_service_info.ppp_user,
            'ringo'
        )
        self.assertEquals(
            contract_service_info.ppp_password,
            'rango'
        )
        self.assertEquals(
            contract_service_info.endpoint_user,
            'connection'
        )
        self.assertEquals(
            contract_service_info.endpoint_password,
            'password'
        )
        self.assertEquals(
            contract.service_partner_id.street,
            self.service_address['street']
        )
        self.assertEquals(
            contract.service_partner_id.zip,
            self.service_address['zip_code']
        )
        self.assertEquals(
            contract.service_partner_id.city,
            self.service_address['city']
        )
        self.assertEquals(
            contract.service_partner_id.state_id.code,
            self.service_address['state']
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'ADSL',
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:XX',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_allow_hyphen_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'ADSL',
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': '-',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        self.assertIn('id', content)
        self.assertTrue(content['id'])

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_allow_empty_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'ADSL',
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': '',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        self.assertIn('id', content)
        self.assertTrue(content['id'])

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_allow_missing_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'ADSL',
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        self.assertIn('id', content)
        self.assertTrue(content['id'])

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_router_product_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'ADSL',
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': 0,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:44',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_not_found_router_product_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'ADSL',
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': 'XXX',
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:44',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    def test_route_right_vodafone_fiber(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "Vodafone",
            "vodafone_fiber_contract_service_info": {
                "phone_number": "654123456",
                'vodafone_offer_code': 'offer',
                'vodafone_id': "123"
            },
            "fiber_signal_type": "NEBAFTTH",
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(
            contract.name,
            data['vodafone_fiber_contract_service_info']['phone_number']
        )
        self.assertTrue(contract.vodafone_fiber_service_contract_info_id)
        contract_service_info = contract.vodafone_fiber_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '654123456')
        self.assertEquals(contract_service_info.vodafone_id, '123')
        self.assertEquals(contract_service_info.vodafone_offer_code, 'offer')
        self.assertEquals(
            contract.service_partner_id.street,
            self.service_address['street']
        )
        self.assertEquals(
            contract.service_partner_id.zip,
            self.service_address['zip_code']
        )
        self.assertEquals(
            contract.service_partner_id.city,
            self.service_address['city']
        )
        self.assertEquals(
            contract.service_partner_id.state_id.code,
            self.service_address['state']
        )
        self.assertEquals(contract.fiber_signal_type_id.code, "NEBAFTTH")

    def test_route_right_mm_fiber(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "MásMóvil",
            "mm_fiber_contract_service_info": {
                "phone_number": "654123456",
                'mm_id': "123"
            },
            "fiber_signal_type": "fibraIndirecta",
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(
            contract.name,
            data['mm_fiber_contract_service_info']['phone_number']
        )
        self.assertTrue(contract.mm_fiber_service_contract_info_id)
        contract_service_info = contract.mm_fiber_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '654123456')
        self.assertEquals(contract_service_info.mm_id, '123')
        self.assertEquals(
            contract.service_partner_id.street,
            self.service_address['street']
        )
        self.assertEquals(
            contract.service_partner_id.zip,
            self.service_address['zip_code']
        )
        self.assertEquals(
            contract.service_partner_id.city,
            self.service_address['city']
        )
        self.assertEquals(
            contract.service_partner_id.state_id.code,
            self.service_address['state']
        )
        self.assertEquals(contract.fiber_signal_type_id.code, "fibraIndirecta")

    def test_route_right_orange_fiber(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "Orange",
            "orange_fiber_contract_service_info": {
                'suma_id': "123"
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(
            contract.name,
            '-'
        )
        self.assertTrue(contract.orange_fiber_service_contract_info_id)
        contract_service_info = contract.orange_fiber_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '-')
        self.assertEquals(contract_service_info.suma_id, '123')
        self.assertEquals(
            contract.service_partner_id.street,
            self.service_address['street']
        )
        self.assertEquals(
            contract.service_partner_id.zip,
            self.service_address['zip_code']
        )
        self.assertEquals(
            contract.service_partner_id.city,
            self.service_address['city']
        )
        self.assertEquals(
            contract.service_partner_id.state_id.code,
            self.service_address['state']
        )

    def test_route_wrong_orange_fiber_without_service_info(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "Orange",
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    def test_route_right_xoln_fiber_la_borda(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                'external_id': "123",
                "id_order": "456",
                "project": "laBorda",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(
            contract.name,
            data['xoln_fiber_contract_service_info']['phone_number']
        )
        self.assertTrue(contract.xoln_fiber_service_contract_info_id)
        contract_service_info = contract.xoln_fiber_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '654123456')
        self.assertEquals(contract_service_info.external_id, '123')
        self.assertEquals(contract_service_info.id_order, '456')
        self.assertEquals(
            contract.service_partner_id.street,
            self.service_address['street']
        )
        self.assertEquals(
            contract.service_partner_id.zip,
            self.service_address['zip_code']
        )
        self.assertEquals(
            contract.service_partner_id.city,
            self.service_address['city']
        )
        self.assertEquals(
            contract.service_partner_id.state_id.code,
            self.service_address['state']
        )
        self.assertEquals(
            contract_service_info.router_lot_id.product_id.id,
            self.router_product.id
        )
        self.assertEquals(
            contract_service_info.router_lot_id.name,
            '4637'
        )
        self.assertEquals(
            contract_service_info.router_lot_id.router_mac_address,
            'AA:BB:CC:22:33:11'
        )

    def test_route_right_xoln_fiber_xarxa_greta(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                'external_id': "123",
                "id_order": "456",
                "project": "xGreta",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "fiber_signal_type": "",
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(
            contract.name,
            data['xoln_fiber_contract_service_info']['phone_number']
        )
        self.assertTrue(contract.xoln_fiber_service_contract_info_id)
        contract_service_info = contract.xoln_fiber_service_contract_info_id
        self.assertEquals(contract_service_info.phone_number, '654123456')
        self.assertEquals(contract_service_info.external_id, '123')
        self.assertEquals(contract_service_info.id_order, '456')
        self.assertEquals(
            contract_service_info.router_lot_id.product_id.id,
            self.router_product.id
        )
        self.assertEquals(
            contract_service_info.router_lot_id.name,
            '4637'
        )
        self.assertEquals(
            contract_service_info.router_lot_id.router_mac_address,
            'AA:BB:CC:22:33:11'
        )
        self.assertEquals(
            contract.service_partner_id.street,
            self.service_address['street']
        )
        self.assertEquals(
            contract.service_partner_id.zip,
            self.service_address['zip_code']
        )
        self.assertEquals(
            contract.service_partner_id.city,
            self.service_address['city']
        )
        self.assertEquals(
            contract.service_partner_id.state_id.code,
            self.service_address['state']
        )
        self.assertFalse(contract.fiber_signal_type_id)

    def test_route_right_vodafone_4G(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": "4G",
            "service_supplier": "Vodafone",
            "router_4G_contract_service_info": {
                "phone_number": "-",
                "vodafone_id": "34564",
                "vodafone_offer_code": "2882582",
                "previous_id": "0004"
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(contract.name, "-")
        self.assertEquals(
            contract.service_partner_id.street,
            self.service_address['street']
        )
        self.assertEquals(
            contract.service_partner_id.zip,
            self.service_address['zip_code']
        )
        self.assertEquals(
            contract.service_partner_id.city,
            self.service_address['city']
        )
        self.assertEquals(
            contract.service_partner_id.state_id.code,
            self.service_address['state']
        )
        contract_service_info = contract.router_4G_service_contract_info_id
        self.assertTrue(contract_service_info)
        self.assertEquals(contract_service_info.phone_number, "-")
        self.assertEquals(contract_service_info.vodafone_id, '34564')
        self.assertEquals(contract_service_info.vodafone_offer_code, '2882582')

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_missing_service_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.ref('base.res_partner_12'),
            "email": self.email,
            "service_technology": 'ADSL',
            "service_supplier": "Jazztel",
            "adsl_contract_service_info": {
                "phone_number": "654123456",
                'administrative_number': '123',
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
                'ppp_user': 'ringo',
                'ppp_password': 'rango',
                'endpoint_user': 'connection',
                'endpoint_password': 'password'
            },
            "contract_lines": [],
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    def test_route_right_create_with_code(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "code": "1234",
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(contract.code, '1234')

    def test_route_right_create_without_code(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        contract_code = self.browse_ref(
            'somconnexio.sequence_contract'
        ).number_next_actual
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertEquals(contract.code, str(contract_code))

    def test_route_right_create_with_new_email(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": "new_email@test.coop",
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])

        self.assertEquals(len(contract.email_ids), 1)
        self.assertEquals(
            contract.email_ids[0].email,
            "new_email@test.coop"
        )
        self.assertEquals(
            contract.email_ids[0].parent_id.id,
            self.browse_ref('somconnexio.res_partner_2_demo').id
        )

    def test_route_right_empty_email(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": "",
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "code": "1234",
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])

        self.assertEquals(
            contract.email_ids[0].email,
            self.email
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_missing_email(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "code": "1234",
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_missing_ticket_number(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_duplicated_ticket_number(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        contract = self.env['contract.contract'].browse(content['id'])
        self.assertTrue(contract)
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_missing_mandate(self, *args):
        self.mandate.unlink()
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_technology": 'Mobile',
            "service_supplier": "MásMóvil",
            "mobile_contract_service_info": {
                "phone_number": "654321123",
                "icc": "123456",
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_id_order(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                'external_id': "123",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_external_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                'id_order': "456",
                "project": "laBorda",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_phone_number(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                'id_order': "456",
                "project": "laBorda",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_project(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                "external_id": "123",
                'id_order': "456",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_not_valid_project(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                'id_order': "456",
                'project': 'XXX',
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_router_product_id(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                'id_order': "456",
                "project": "laBorda",
                "phone_number": "654123456",
                'router_serial_number': '4637',
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_router_serial_number(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                'id_order': "456",
                "project": "laBorda",
                "phone_number": "654123456",
                'router_product_id': self.router_product.default_code,
                'router_mac_address': 'AA:BB:CC:22:33:11',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        self.assertRaises(UserError, process.create, **data)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_fiber_xoln_missing_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "external_id": "123",
                'id_order': "456",
                "project": "laBorda",
                "phone_number": "654123456",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        self.assertIn('id', content)
        self.assertTrue(content['id'])

    def test_route_right_xoln_empty_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                'external_id': "123",
                "id_order": "456",
                "project": "laBorda",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': ''
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        self.assertIn('id', content)
        self.assertTrue(content['id'])

    def test_route_right_xoln_hyphen_mac_address(self, *args):
        url = "/public-api/contract"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
            "service_address": self.service_address,
            "service_technology": 'Fiber',
            "service_supplier": "XOLN",
            "xoln_fiber_contract_service_info": {
                "phone_number": "654123456",
                'external_id': "123",
                "id_order": "456",
                "project": "laBorda",
                'router_product_id': self.router_product.default_code,
                'router_serial_number': '4637',
                'router_mac_address': '-'
            },
            "contract_lines": [],
            "iban": self.iban,
            "ticket_number": self.ticket_number
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractContractProcess(self.env)
        content = process.create(**data)
        self.assertIn('id', content)
        self.assertTrue(content['id'])


class TestContractCountController(BaseEMCRestCaseAdmin):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env['contract.contract']
        self.Partner = self.env['res.partner']
        vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        partner = self.browse_ref('somconnexio.res_partner_2_demo')
        partner_id = partner.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        product_ref = self.browse_ref('somconnexio.Fibra100Mb')
        product = self.env["product.product"].search(
            [('default_code', '=', product_ref.default_code)]
        )
        self.contract_line = {
            "name": product.name,
            "product_id": product.id,
            "date_start": "2020-01-01 00:00:00",
            "recurring_next_date": date.today() + timedelta(days=30),
        }
        self.vals_contract = {
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
                vodafone_fiber_contract_service_info.id
            ),
            'bank_id': partner.bank_ids.id,
            'contract_line_ids': [
                (0, False, self.contract_line)
            ]

        }
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
            'iban': 'ES6020808687312159493841',
            'state': 'done'
        }

    def test_route_count_one_contract_active(self, *args):
        url = "/public-api/contract-count"
        count_contract = self.env['contract.contract'].search_count([])
        self.Contract.unlink()
        self.assertEquals(count_contract, 0)
        self.Contract.create(self.vals_contract)
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertIn('contracts', decoded_response)
        self.assertEquals(decoded_response["contracts"], 1)

    def test_route_doesnt_count_one_contract_terminated(self, *args):
        url = "/public-api/contract-count"
        count_contract = self.env['contract.contract'].search_count([])
        self.Contract.unlink()
        self.assertEquals(count_contract, 0)
        self.vals_contract['is_terminated'] = True
        self.Contract.create(self.vals_contract)
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertIn('contracts', decoded_response)
        self.assertEquals(decoded_response["contracts"], 0)

    def test_route_count_one_member(self, *args):
        url = "/public-api/contract-count"
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertIn('members', decoded_response)
        count_members = decoded_response['members']
        self.Partner.create({
            'name': 'test member', 'member': True, 'coop_candidate': False,
            'customer': True
        })
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertIn('members', decoded_response)
        self.assertEquals(decoded_response["members"]-count_members, 1)

    def test_route_count_one_coop_candidate(self, *args):
        url = "/public-api/contract-count"
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertIn('members', decoded_response)
        count_members = decoded_response['members']
        partner = self.Partner.create({
            'name': 'test member', 'coop_candidate': True, 'customer': True
        })
        self.vals_subscription['partner_id'] = partner.id
        self.env['subscription.request'].create(self.vals_subscription)
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertIn('members', decoded_response)
        self.assertEquals(decoded_response["members"]-count_members, 1)

    def test_route_doesnt_count_one_partner_not_member(self, *args):
        url = "/public-api/contract-count"
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertIn('members', decoded_response)
        count_members = decoded_response['members']
        self.Partner.create({
            'name': 'test member', 'member': False, 'coop_candidate': False,
            'customer': True
        })
        response = self.http_get(url)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertIn('members', decoded_response)
        self.assertEquals(decoded_response["members"]-count_members, 0)
