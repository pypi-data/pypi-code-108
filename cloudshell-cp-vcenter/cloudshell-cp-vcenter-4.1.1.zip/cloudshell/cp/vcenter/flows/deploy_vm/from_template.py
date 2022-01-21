from cloudshell.cp.core.request_actions.models import VmDetailsData

from cloudshell.cp.vcenter.actions.validation import ValidationActions
from cloudshell.cp.vcenter.actions.vm_details import VMDetailsActions
from cloudshell.cp.vcenter.flows.deploy_vm.base_flow import (
    AbstractVCenterDeployVMFromTemplateFlow,
)
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.models.deploy_app import VMFromTemplateDeployApp


class VCenterDeployVMFromTemplateFlow(AbstractVCenterDeployVMFromTemplateFlow):
    def _get_vm_template(
        self, deploy_app: VMFromTemplateDeployApp, dc: DcHandler
    ) -> VmHandler:
        """Get VM template to clone VM from."""
        return dc.get_vm_by_path(deploy_app.vcenter_template)

    def _validate_deploy_app(self, deploy_app: VMFromTemplateDeployApp):
        """Validate Deploy App before deployment."""
        super()._validate_deploy_app(deploy_app)

        validation_actions = ValidationActions(
            self._si,
            self._resource_config,
            self._logger,
        )
        validation_actions.validate_deploy_app_from_template(deploy_app)

    def _prepare_vm_details_data(
        self, deployed_vm: VmHandler, deploy_app: VMFromTemplateDeployApp
    ) -> VmDetailsData:
        """Prepare CloudShell VM Details model."""
        vm_details_actions = VMDetailsActions(
            self._si,
            self._resource_config,
            self._logger,
            self._cancellation_manager,
        )
        return vm_details_actions.create(deployed_vm, deploy_app)
