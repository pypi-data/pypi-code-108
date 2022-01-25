from odoo.addons.component.core import Component
from odoo.addons.base_rest.components.service import skip_secure_params
from odoo.addons.base_rest.components.service import skip_secure_response


class AccountInvoiceService(Component):
    _inherit = "account.invoice.service"

    @skip_secure_response
    @skip_secure_params
    def create(self, **params):
        self.env['account.invoice'].with_delay(
            priority=30
        ).create_invoice(**params)
        return {"result": "OK"}
