import logging

from odoo.addons.component.core import Component

from . import schemas

_logger = logging.getLogger(__name__)


class ProviderService(Component):
    _inherit = "base.rest.service"
    _name = "provider.services"
    _usage = "provider"
    _collection = "emc.services"
    _description = """
        Provider service to expose the providers list filtering by service.
    """

    def search(self, mobile=None, broadband=None):
        domain = []

        if mobile == "true":
            domain.append(("mobile", "=", True))
        if broadband == "true":
            domain.append(("broadband", "=", True))

        _logger.info("search with domain {}".format(domain))
        requests = self.env["previous.provider"].search(domain)

        response = {
            "count": len(requests),
            "providers": [self._to_dict(sr) for sr in requests],
        }
        return response

    def _to_dict(self, sr):
        sr.ensure_one()
        return {
            "id": sr.id,
            "name": sr.name
        }

    def _validator_search(self):
        return schemas.S_PREVIOUS_PROVIDER_REQUEST_SEARCH

    def _validator_return_search(self):
        return schemas.S_PREVIOUS_PROVIDER_RETURN_SEARCH
