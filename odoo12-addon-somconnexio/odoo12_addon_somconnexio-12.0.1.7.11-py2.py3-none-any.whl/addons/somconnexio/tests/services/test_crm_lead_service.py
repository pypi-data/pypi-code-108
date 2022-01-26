import json

import odoo

from ..common_service import BaseEMCRestCaseAdmin


class CRMLeadServiceRestCase(BaseEMCRestCaseAdmin):

    def setUp(self):
        super().setUp()
        self.partner = self.browse_ref('somconnexio.res_partner_1_demo')

    def test_route_right_create(self):
        url = "/api/crm-lead"
        data = {
            "iban": "ES6621000418401234567891",
            "subscription_request_id": self.browse_ref(
                "easy_my_coop.subscription_request_1_demo")._api_external_id,
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B"
                        },
                        "invoice_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B"
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract"
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead, = self.env["crm.lead"].browse(content["id"])
        self.assertEquals(crm_lead.iban, data["iban"])
        self.assertEquals(
            crm_lead.subscription_request_id.id,
            self.browse_ref("easy_my_coop.subscription_request_1_demo").id
        )
        self.assertEquals(
            len(crm_lead.lead_line_ids),
            1
        )
        self.assertEquals(
            crm_lead.mobile_lead_line_id.mobile_isp_info.phone_number,
            '123'
        )
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEquals(
            crm_lead_line.product_id.id,
            self.browse_ref('somconnexio.150Min1GB').id
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.icc_donor,
            "123",
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.type,
            "portability",
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_full_street,
            "Carrer del Rec 123",
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_city,
            "Barcelona",
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_zip_code,
            "08000",
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_country_id.id,
            self.browse_ref('base.es').id
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_state_id.id,
            self.browse_ref('base.state_es_b').id
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_full_street,
            "Carrer del Rec 123",
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_city,
            "Barcelona",
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_zip_code,
            "08000",
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_country_id.id,
            self.browse_ref('base.es').id
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.invoice_state_id.id,
            self.browse_ref('base.state_es_b').id
        )

    def test_route_right_create_with_partner_id(self):
        url = "/api/crm-lead"
        data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B"
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract"
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead, = self.env["crm.lead"].browse(content["id"])
        self.assertEquals(
            crm_lead.partner_id.ref,
            self.partner.ref
        )

    def test_route_right_create_with_icc(self):
        url = "/api/crm-lead"
        data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "icc": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B"
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract"
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead, = self.env["crm.lead"].browse(content["id"])
        self.assertTrue(crm_lead.mobile_lead_line_id.mobile_isp_info.has_sim)

    def test_route_right_create_with_partner_id_without_previous_owner(self):
        url = "/api/crm-lead"
        data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B"
                        },
                        "previous_provider": 1,
                        "previous_contract_type": "contract"
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead, = self.env["crm.lead"].browse(content["id"])
        self.assertEquals(
            crm_lead.partner_id.ref,
            self.partner.ref
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_subscription_request_id_create(self):
        url = "/api/crm-lead"
        data = {
            "subscription_request_id": 666,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B"
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract"
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(error_msg, "SubscriptionRequest with id 666 not found")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_mobile_isp_info_create(self):
        url = "/api/crm-lead"
        data = {
            "subscription_request_id": self.browse_ref(
                "easy_my_coop.subscription_request_1_demo").id,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {},
                    "broadband_isp_info": {}
                }
            ]
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(
            error_msg,
            "Mobile product SE_SC_REC_MOBILE_T_150_1024 needs a mobile_isp_info"
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_broadband_isp_info_create(self):
        url = "/api/crm-lead"
        data = {
            "subscription_request_id": self.browse_ref(
                "easy_my_coop.subscription_request_1_demo").id,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.ADSL20MBSenseFix').default_code
                    ),
                    "mobile_isp_info": {},
                    "broadband_isp_info": {}
                }
            ]
        }
        response = self.http_post(url, data=data)
        self.assertEquals(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(
            error_msg,
            "Broadband product SE_SC_REC_BA_ADSL_SF needs a broadband_isp_info"
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_subcription_and_partner_ids(self):
        url = "/api/crm-lead"
        data = {
            "subscription_request_id": self.ref(
                "easy_my_coop.subscription_request_1_demo"),
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B"
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract"
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 400)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_wrong_without_iban(self):
        url = "/api/crm-lead"
        data = {
            "subscription_request_id": self.browse_ref(
                "easy_my_coop.subscription_request_1_demo").id,
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "delivery_address": {
                            "street": "Carrer del Rec",
                            "street2": "123",
                            "zip_code": "08000",
                            "city": "Barcelona",
                            "country": "ES",
                            "state": "B"
                        },
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract"
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 400)

    def test_route_right_create_with_partner_id_wo_delivery_address(self):
        url = "/api/crm-lead"
        data = {
            "partner_id": self.partner.ref,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc_donor": "123",
                        "phone_number": "123",
                        "type": "portability",
                        "previous_provider": 1,
                        "previous_owner_name": "Newus",
                        "previous_owner_first_name": "Borgo",
                        "previous_owner_vat_number": "29461336S",
                        "previous_contract_type": "contract"
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead, = self.env["crm.lead"].browse(content["id"])
        self.assertEquals(
            crm_lead.partner_id.ref,
            self.partner.ref
        )
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_street,
            self.partner.street,
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_city,
            self.partner.city,
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_zip_code,
            self.partner.zip,
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_country_id,
            self.partner.country_id
        )
        self.assertEquals(
            crm_lead_line.mobile_isp_info.delivery_state_id,
            self.partner.state_id
        )

    def test_route_right_create_wo_partner_id_wo_delivery_address_w_icc(self):
        url = "/api/crm-lead"
        data = {
            "subscription_request_id": self.browse_ref(
                "easy_my_coop.subscription_request_1_demo")._api_external_id,
            "iban": "ES6621000418401234567891",
            "lead_line_ids": [
                {
                    "product_code": (
                        self.browse_ref('somconnexio.150Min1GB').default_code
                    ),
                    "mobile_isp_info": {
                        "icc": "123",
                        "type": "new",
                    },
                    "broadband_isp_info": {}
                }
            ]
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead, = self.env["crm.lead"].browse(content["id"])
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEquals(
            crm_lead_line.mobile_isp_info.icc,
            "123",
        )
