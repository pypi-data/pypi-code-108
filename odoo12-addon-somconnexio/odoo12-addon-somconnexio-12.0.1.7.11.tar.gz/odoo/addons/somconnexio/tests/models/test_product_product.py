from ..sc_test_case import SCTestCase


class TestStockProductionLot(SCTestCase):
    def test_product_wo_catalog_name(self):
        product = self.browse_ref('somconnexio.Fibra100Mb')
        self.assertFalse(product.get_catalog_name('Min BA'))

    def test_product_catalog_name_in_template(self):
        product = self.browse_ref('somconnexio.100MinSenseDades')
        # noupdate=1 in product_attribute_value.xml
        product.product_tmpl_id.catalog_attribute_id.catalog_name = '100'
        self.assertEquals(product.get_catalog_name('Min'), '100')

    def test_product_catalog_name_in_product(self):
        product = self.browse_ref('somconnexio.100MinSenseDades')
        # noupdate=1 in product_attribute_value.xml
        product.attribute_value_ids.catalog_name = '0'
        self.assertEquals(product.get_catalog_name('Data'), '0')
