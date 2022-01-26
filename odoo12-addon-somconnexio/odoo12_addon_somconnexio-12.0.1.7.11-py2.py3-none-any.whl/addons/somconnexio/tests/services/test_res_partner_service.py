import json
import odoo

from ..common_service import BaseEMCRestCaseAdmin


class TestResPartnerController(BaseEMCRestCaseAdmin):

    def setUp(self):
        super().setUp()

        self.url = "/api/partner"

    @odoo.tools.mute_logger("odoo.addons.auth_api_key.models.ir_http")
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_raise_error_without_auth(self):
        response = self.http_get_without_auth()

        self.assertEquals(response.status_code, 403)
        self.assertEquals(response.reason, "FORBIDDEN")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_without_ref(self):
        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.reason, "BAD REQUEST")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_not_found(self):
        response = self.http_get(
            "{}/{}".format(self.url, 123)
        )

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    def test_route_get(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")

        response = self.http_get(
            "{}/{}".format(self.url, int(partner.ref))
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content["id"], partner.id)
        self.assertEqual(content["name"], partner.name)
        self.assertEqual(content["ref"], partner.ref)
        self.assertEqual(
            content["cooperator_register_number"],
            partner.cooperator_register_number
        )
        self.assertEqual(
            content["cooperator_end_date"],
            ""
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_search_not_found(self):
        response = self.http_get(
            "{}?vat={}".format(self.url, "66758531L")
        )

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    def test_route_search(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")

        response = self.http_get(
            "{}?vat={}".format(self.url, partner.vat)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content["id"], partner.id)
        self.assertEqual(content["name"], partner.name)
        self.assertEqual(content["ref"], partner.ref)
        self.assertEqual(
            content["cooperator_register_number"],
            partner.cooperator_register_number
        )
        self.assertEqual(
            content["cooperator_end_date"],
            ""
        )
        self.assertFalse(content["coop_candidate"])
        self.assertTrue(content["member"])

    def test_route_search_normalize_vat(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")

        bad_formatted_vat = "  {}---. ".format(partner.vat)
        response = self.http_get(
            "{}?vat={}".format(self.url, bad_formatted_vat)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content["id"], partner.id)
