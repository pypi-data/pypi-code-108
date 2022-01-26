from logging import Logger

import attr

from cloudshell.shell.core.driver_context import AutoLoadDetails

from cloudshell.cp.vcenter.actions.validation import ValidationActions
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.vsphere_sdk_handler import VSphereSDKHandler
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


@attr.s(auto_attribs=True)
class VCenterAutoloadFlow:
    _resource_config: VCenterResourceConfig
    _logger: Logger

    def discover(self) -> AutoLoadDetails:
        si = SiHandler.from_config(self._resource_config, self._logger)
        validation_actions = ValidationActions(si, self._resource_config, self._logger)
        validation_actions.validate_resource_conf()
        validation_actions.validate_resource_conf_dc_objects()

        vsphere_client = VSphereSDKHandler.from_config(
            resource_config=self._resource_config,
            reservation_info=None,
            logger=self._logger,
        )
        if vsphere_client is not None:
            vsphere_client.create_categories()

        return AutoLoadDetails([], [])
