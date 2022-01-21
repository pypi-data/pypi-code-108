from datetime import datetime
from logging import Logger

import attr

from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.models.deployed_app import BaseVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import ShutdownMethod, VCenterResourceConfig


@attr.s(auto_attribs=True)
class VCenterPowerFlow:
    _deployed_app: BaseVCenterDeployedApp
    _resource_config: VCenterResourceConfig
    _logger: Logger

    def _get_vm(self, si: SiHandler) -> VmHandler:
        self._logger.info(f"Getting VM by its UUID {self._deployed_app.vmdetails.uid}")
        dc = DcHandler.get_dc(self._resource_config.default_datacenter, si)
        return dc.get_vm_by_uuid(self._deployed_app.vmdetails.uid)

    def power_on(self):
        si = SiHandler.from_config(self._resource_config, self._logger)
        vm = self._get_vm(si)

        self._logger.info(f"Powering On the {vm}")
        spec_name = vm.name
        spec = si.get_customization_spec(spec_name)
        if spec:
            self._logger.info(f"Adding Customization Spec to the {vm}")
            vm.add_customization_spec(spec, self._logger)
        else:
            self._logger.info(f"No VM Customization Spec found, powering on the {vm}")

        begin_time = datetime.now()
        vm.power_on(self._logger)

        if spec:
            vm.wait_for_customization_ready(begin_time, self._logger)
            si.delete_customization_spec(spec_name)

    def power_off(self):
        si = SiHandler.from_config(self._resource_config, self._logger)
        vm = self._get_vm(si)
        self._logger.info(f"Powering Off {vm}")
        soft = self._resource_config.shutdown_method is ShutdownMethod.SOFT
        vm.power_off(soft, self._logger)
