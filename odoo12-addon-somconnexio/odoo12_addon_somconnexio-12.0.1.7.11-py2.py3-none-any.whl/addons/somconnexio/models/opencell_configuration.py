import logging
logger = logging.getLogger(__name__)


class OpenCellConfigurationWrapper:

    def __init__(self, env):
        self.env = env

    def get_configuration(self):
        return self.env['ir.config_parameter']


class OpenCellConfiguration:

    def __init__(self, env):
        self.configuration_wrapper = OpenCellConfigurationWrapper(env)

    @property
    def seller_code(self):
        return self.configuration_wrapper.get_configuration().get_param(
            'somconnexio.opencell_seller_code'
        )

    @property
    def customer_category_code(self):
        return self.configuration_wrapper.get_configuration().get_param(
            'somconnexio.opencell_customer_category_code'
        )
