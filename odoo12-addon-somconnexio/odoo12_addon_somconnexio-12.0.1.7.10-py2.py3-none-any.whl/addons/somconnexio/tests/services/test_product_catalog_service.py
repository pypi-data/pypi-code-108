import json
from ..common_service import BaseEMCRestCaseAdmin


class TestProductCatalogController(BaseEMCRestCaseAdmin):

    def setUp(self):
        super().setUp()
        self.url = "/api/product-catalog"
        self.code = "0IVA"
        self.product = self.browse_ref('somconnexio.150Min1GB')
        self.product.product_tmpl_id.catalog_attribute_id = (
            self.browse_ref('somconnexio.150Min')
        )
        self.product.product_tmpl_id.catalog_attribute_id.catalog_name = (
            "150"
        )
        self.product.attribute_value_ids.catalog_name = '1024'
        self.product.public = True
        self.demo_pricelist = self.browse_ref('somconnexio.pricelist_without_IVA')

    def _get_service_products(self):
        service_product_templates = self.env["product.template"].search([
            ("categ_id", 'in', [
                self.env.ref('somconnexio.mobile_service').id,
                self.env.ref('somconnexio.broadband_adsl_service').id,
                self.env.ref('somconnexio.broadband_fiber_service').id,
                ])
        ])
        service_products = self.env["product.product"].search([
            ("product_tmpl_id", 'in', [tmpl.id for tmpl in service_product_templates]),
            ("public", '=', True),
        ])
        return service_products

    def test_route(self):
        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

    def test_price_list_count(self):
        response = self.http_get(self.url)
        content = json.loads(response.content.decode("utf-8"))

        # DEMO pricelist 'pricelist_without_IVA'
        self.assertEqual(len(content["pricelists"]), 1)

    def test_price_list_content(self):
        expected_mobile_product_info = {
            "code": self.product.default_code,
            "name": self.product.showed_name,
            "price": self.product.with_context(pricelist=self.demo_pricelist.id).price,
            "category": "mobile",
            "minutes": 150,
            "data": 1024,
            "bandwidth": None,
            "available_for": [
                "member",
                "coop_agreement",
                "sponsored",
            ],
        }
        fiber_product = self.browse_ref('somconnexio.Fibra600Mb')
        fiber_product.attribute_value_ids.catalog_name = '600'
        fiber_product.public = True
        expected_fiber_product_info = {
            "code": fiber_product.default_code,
            "name": fiber_product.showed_name,
            "price": fiber_product.with_context(pricelist=self.demo_pricelist.id).price,
            "category": "fiber",
            "minutes": None,
            "data": None,
            "bandwidth": 600,
            "available_for": [
                "member",
            ],
        }
        adsl_product = self.browse_ref('somconnexio.ADSL20MBSenseFix')
        adsl_product.public = True
        expected_adsl_product_info = {
            "code": adsl_product.default_code,
            "name": adsl_product.showed_name,
            "price": adsl_product.with_context(pricelist=self.demo_pricelist.id).price,
            "category": "adsl",
            "minutes": None,
            "data": None,
            "bandwidth": 20,
            "available_for": [
                "member",
                "coop_agreement",
            ],
        }
        response = self.http_get(self.url)
        content = json.loads(response.content.decode("utf-8"))

        obtained_pricelist = content.get("pricelists")[0].get('products')
        service_products = self._get_service_products()

        self.assertEqual(
            len(service_products),
            len(obtained_pricelist)
        )
        self.assertTrue(expected_mobile_product_info in obtained_pricelist)
        self.assertTrue(expected_fiber_product_info in obtained_pricelist)
        self.assertTrue(expected_adsl_product_info in obtained_pricelist)

    def test_search_by_code(self):
        code = "new-fake-code"
        self.env["product.pricelist"].create({
            "code": code,
            "name": "test pricelist",
            "currency_id": 1
        })

        response = self.http_get("{}?code={}".format(self.url, code))
        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelists = content.get("pricelists")
        self.assertEqual(len(obtained_pricelists), 1)
        self.assertEqual(obtained_pricelists[0].get("code"), code)

    def test_search_by_category(self):
        mobile_products_templ_ids = self.env["product.template"].search([
            ("categ_id", '=', self.env.ref('somconnexio.mobile_service').id)
        ])
        mobile_products = self.env["product.product"].search([
            ("product_tmpl_id", 'in', [tmpl.id for tmpl in mobile_products_templ_ids]),
            ("public", '=', True)
        ])

        response = self.http_get("{}?categ=mobile".format(self.url))
        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelists = content.get("pricelists")
        obtained_mobile_catalog = obtained_pricelists[0].get("products")
        self.assertEqual(len(obtained_pricelists), 1)
        self.assertEqual(len(obtained_mobile_catalog), len(mobile_products))
        self.assertEqual(obtained_mobile_catalog[0]["category"], "mobile")

    def test_search_catalan(self):
        expected_mobile_product_info = {
            "code": self.product.default_code,
            "name": self.product.showed_name,
            "price": self.product.with_context(pricelist=self.demo_pricelist.id).price,
            "category": "mobile",
            "minutes": 150,
            "data": 1024,
            "bandwidth": None,
            "available_for": [
                "member",
                "coop_agreement",
                "sponsored",
            ],
        }
        fiber_product = self.browse_ref('somconnexio.Fibra600Mb')
        fiber_product.attribute_value_ids.catalog_name = '600'
        fiber_product.public = True
        expected_fiber_product_info = {
            "code": fiber_product.default_code,
            "name": fiber_product.showed_name,
            "price": fiber_product.with_context(pricelist=self.demo_pricelist.id).price,
            "category": "fiber",
            "minutes": None,
            "data": None,
            "bandwidth": 600,
            "available_for": [
                "member",
            ],
        }
        adsl_product = self.browse_ref('somconnexio.ADSL20MBSenseFix')
        adsl_product.public = True
        expected_adsl_product_info = {
            "code": adsl_product.default_code,
            "name": adsl_product.showed_name,
            "price": adsl_product.with_context(pricelist=self.demo_pricelist.id).price,
            "category": "adsl",
            "minutes": None,
            "data": None,
            "bandwidth": 20,
            "available_for": [
                "member",
                "coop_agreement",
            ],
        }
        response = self.http_get(self.url, headers={'Accept-Language': 'ca_ES'})
        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelist = content.get("pricelists")[0].get('products')
        service_products = self._get_service_products()

        self.assertEqual(
            len(service_products),
            len(obtained_pricelist)
        )
        self.assertTrue(expected_mobile_product_info in obtained_pricelist)
        self.assertTrue(expected_fiber_product_info in obtained_pricelist)
        self.assertTrue(expected_adsl_product_info in obtained_pricelist)
