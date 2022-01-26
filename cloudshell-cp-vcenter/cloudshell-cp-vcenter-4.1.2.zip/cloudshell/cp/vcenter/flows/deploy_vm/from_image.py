from cloudshell.cp.core.request_actions.models import VmDetailsData

from cloudshell.cp.vcenter.actions.validation import ValidationActions
from cloudshell.cp.vcenter.actions.vm_details import VMDetailsActions
from cloudshell.cp.vcenter.flows.deploy_vm.base_flow import AbstractVCenterDeployVMFlow
from cloudshell.cp.vcenter.flows.deploy_vm.commands.deploy_vm_from_image import (
    DeployVMFromImageCommand,
)
from cloudshell.cp.vcenter.handlers.datastore_handler import DatastoreHandler
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.folder_handler import FolderHandler
from cloudshell.cp.vcenter.handlers.resource_pool import ResourcePoolHandler
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.models.deploy_app import VMFromImageDeployApp


class VCenterDeployVMFromImageFlow(AbstractVCenterDeployVMFlow):
    def _validate_deploy_app(self, deploy_app: VMFromImageDeployApp):
        """Validate Deploy App before deployment."""
        super()._validate_deploy_app(deploy_app)

        validation_actions = ValidationActions(
            self._si,
            self._resource_config,
            self._logger,
        )
        validation_actions.validate_deploy_app_from_image(deploy_app)
        validation_actions.validate_ovf_tool(self._resource_config.ovf_tool_path)

    def _prepare_vm_details_data(
        self, deployed_vm: VmHandler, deploy_app: VMFromImageDeployApp
    ) -> VmDetailsData:
        """Prepare CloudShell VM Details model."""
        vm_details_actions = VMDetailsActions(
            self._si,
            self._resource_config,
            self._logger,
            self._cancellation_manager,
        )
        return vm_details_actions.create(deployed_vm, deploy_app)

    def _create_vm(
        self,
        deploy_app: VMFromImageDeployApp,
        vm_name: str,
        vm_resource_pool: ResourcePoolHandler,
        vm_storage: DatastoreHandler,
        vm_folder: FolderHandler,
        dc: DcHandler,
    ):
        """Create VM on the vCenter."""
        vm_folder_path = self._prepare_vm_folder_path(deploy_app)

        return DeployVMFromImageCommand(
            rollback_manager=self._rollback_manager,
            cancellation_manager=self._cancellation_manager,
            resource_conf=self._resource_config,
            vcenter_image=deploy_app.vcenter_image,
            vcenter_image_arguments=deploy_app.vcenter_image_arguments,
            vm_name=vm_name,
            vm_resource_pool=vm_resource_pool,
            vm_storage=vm_storage,
            vm_folder_path=vm_folder_path,
            dc=dc,
            logger=self._logger,
        ).execute()
