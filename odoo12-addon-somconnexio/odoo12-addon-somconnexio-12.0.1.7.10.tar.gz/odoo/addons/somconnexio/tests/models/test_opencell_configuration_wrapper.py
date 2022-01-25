import mock
from odoo.tests.common import TransactionCase
from ..factories import OpenCellConfigurationFactory
from ...models.opencell_configuration import (
    OpenCellConfiguration, OpenCellConfigurationWrapper
)


class OpenCellConfigurationWrapperTests(TransactionCase):

    def test_get_configurarion_gets_expected_tryton_model(self):
        env_mock = mock.MagicMock()
        wrapper = OpenCellConfigurationWrapper(env_mock)
        wrapper.get_configuration()
        env_mock.__getitem__.assert_called_with("ir.config_parameter")


class ExpectedOpenCellConfigurationWrapper:
    def __init__(self, _):
        self.configuration = OpenCellConfigurationFactory()
        self.configuration.get_param = lambda p: (
            self.configuration.seller_code
            if p == 'somconnexio.opencell_seller_code'
            else self.configuration.customer_category_code
        )

    def get_configuration(self):
        return self.configuration


class OpenCellConfigurationTests(TransactionCase):

    def setUp(self):
        with mock.patch(
            "odoo.addons.somconnexio.models."
            "opencell_configuration.OpenCellConfigurationWrapper",
            ExpectedOpenCellConfigurationWrapper
        ):
            self.opencell_configuration = OpenCellConfiguration(mock.ANY)
        self.expected_opencell_configuration_wrapper = (
            self.opencell_configuration.configuration_wrapper
        )

    def test_seller_code(self):
        self.assertEquals(
            self.opencell_configuration.seller_code,
            self.expected_opencell_configuration_wrapper.get_configuration(
            ).seller_code
        )

    def test_customer_category_code(self):
        self.assertEquals(
            self.opencell_configuration.customer_category_code,
            self.expected_opencell_configuration_wrapper.get_configuration(
            ).customer_category_code
        )


class OpencellIrConfigParameters(TransactionCase):

    def setUp(self):
        super().setUp()
        self.opencell_configuration = OpenCellConfiguration(self.env)

    def test_seller_code(self):
        seller_code = self.opencell_configuration.seller_code
        self.assertEquals(
            seller_code,
            'SC'
        )

    def test_customer_category_code(self):
        customer_category_code = self.opencell_configuration.customer_category_code
        self.assertEquals(
            customer_category_code,
            'CLIENT'
        )
