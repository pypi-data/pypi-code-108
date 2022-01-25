import logging

from odoo import _
from odoo.addons.component.core import Component

from . import schemas

_logger = logging.getLogger(__name__)


class DiscoveryChannelService(Component):
    _inherit = "base.rest.service"
    _name = "discovery.channel.service"
    _usage = "discovery-channel"
    _collection = "emc.services"
    _description = """
        Discovery channel service to expose all the categories by which customers
        could have known SomConnexió.
    """

    def search(self):

        _logger.info("searching all discovery channel instances")
        requests = self.env["discovery.channel"].search([])

        response = {
            "discovery_channels": [self._to_dict(dc) for dc in requests],
        }
        return response

    def _to_dict(self, dc):
        dc.ensure_one()
        return {
            "id": dc.id,
            "name": _(dc.name)
        }

    def _validator_search(self):
        return schemas.S_DISCOVERY_CHANNEL_REQUEST_SEARCH

    def _validator_return_search(self):
        return schemas.S_DISCOVERY_CHANNEL_RETURN_SEARCH
