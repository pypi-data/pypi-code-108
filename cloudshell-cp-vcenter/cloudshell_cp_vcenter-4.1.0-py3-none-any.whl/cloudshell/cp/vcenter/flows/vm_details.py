from logging import Logger

from cloudshell.cp.core.cancellation_manager import CancellationContextManager
from cloudshell.cp.core.flows import AbstractVMDetailsFlow
from cloudshell.cp.core.request_actions.models import VmDetailsData

from cloudshell.cp.vcenter.actions.vm_details import VMDetailsActions
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.models.deployed_app import BaseVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


class VCenterGetVMDetailsFlow(AbstractVMDetailsFlow):
    def __init__(
        self,
        resource_conf: VCenterResourceConfig,
        cancellation_manager: CancellationContextManager,
        logger: Logger,
    ):
        super().__init__(logger)
        self._resource_conf = resource_conf
        self._cancellation_manager = cancellation_manager

    def _get_vm_details(self, deployed_app: BaseVCenterDeployedApp) -> VmDetailsData:
        si = SiHandler.from_config(self._resource_conf, self._logger)
        dc = DcHandler.get_dc(self._resource_conf.default_datacenter, si)
        vm = dc.get_vm_by_uuid(deployed_app.vmdetails.uid)
        return VMDetailsActions(
            si,
            self._resource_conf,
            self._logger,
            self._cancellation_manager,
        ).create(vm, deployed_app)
