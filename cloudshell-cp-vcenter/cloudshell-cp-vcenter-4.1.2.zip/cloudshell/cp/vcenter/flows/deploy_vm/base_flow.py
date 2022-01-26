from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from cloudshell.cp.core.flows.deploy import AbstractDeployFlow
from cloudshell.cp.core.request_actions.models import DeployAppResult, VmDetailsData
from cloudshell.cp.core.rollback import RollbackCommandsManager
from cloudshell.cp.core.utils.name_generator import generate_name

from cloudshell.cp.vcenter.actions.validation import ValidationActions
from cloudshell.cp.vcenter.flows.deploy_vm.commands.clone_vm import CloneVMCommand
from cloudshell.cp.vcenter.handlers.config_spec_handler import ConfigSpecHandler
from cloudshell.cp.vcenter.handlers.custom_spec_handler import (
    CustomSpecHandler,
    create_custom_spec_from_spec_params,
)
from cloudshell.cp.vcenter.handlers.datastore_handler import DatastoreHandler
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.folder_handler import FolderHandler
from cloudshell.cp.vcenter.handlers.resource_pool import ResourcePoolHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.snapshot_handler import SnapshotHandler
from cloudshell.cp.vcenter.handlers.vcenter_path import VcenterPath
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.handlers.vsphere_sdk_handler import VSphereSDKHandler
from cloudshell.cp.vcenter.models.custom_spec import get_custom_spec_params
from cloudshell.cp.vcenter.utils.task_waiter import VcenterCancellationContextTaskWaiter
from cloudshell.cp.vcenter.utils.vm_helpers import get_vm_folder_path

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.api.cloudshell_api import CloudShellAPISession
    from cloudshell.cp.core.cancellation_manager import CancellationContextManager
    from cloudshell.cp.core.request_actions import DeployVMRequestActions
    from cloudshell.cp.core.reservation_info import ReservationInfo

    from cloudshell.cp.vcenter.models.deploy_app import BaseVCenterDeployApp
    from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


class AbstractVCenterDeployVMFlow(AbstractDeployFlow):
    def __init__(
        self,
        resource_config: VCenterResourceConfig,
        cs_api: CloudShellAPISession,
        reservation_info: ReservationInfo,
        cancellation_manager: CancellationContextManager,
        logger: Logger,
    ):
        super().__init__(logger=logger)
        self._resource_config = resource_config
        self._reservation_info = reservation_info
        self._cs_api = cs_api
        self._cancellation_manager = cancellation_manager
        self._rollback_manager = RollbackCommandsManager(logger=self._logger)
        self._task_waiter = VcenterCancellationContextTaskWaiter(
            cancellation_manager=cancellation_manager, logger=self._logger
        )
        self._si = SiHandler.from_config(resource_config, logger)
        self._vsphere_client = VSphereSDKHandler.from_config(
            resource_config=self._resource_config,
            reservation_info=self._reservation_info,
            logger=self._logger,
        )

    @abstractmethod
    def _prepare_vm_details_data(
        self, deployed_vm: VmHandler, deploy_app: BaseVCenterDeployApp
    ) -> VmDetailsData:
        """Prepare CloudShell VM Details model."""
        pass

    @abstractmethod
    def _create_vm(
        self,
        deploy_app: BaseVCenterDeployApp,
        vm_name: str,
        vm_resource_pool: ResourcePoolHandler,
        vm_storage: DatastoreHandler,
        vm_folder: FolderHandler,
        dc: DcHandler,
    ) -> VmHandler:
        """Create VM on the vCenter."""
        pass

    def _validate_deploy_app(self, deploy_app: BaseVCenterDeployApp) -> None:
        """Validate Deploy App before deployment."""
        self._logger.info("Validating Deploy App data")

        validation_actions = ValidationActions(
            self._si,
            self._resource_config,
            self._logger,
        )
        validation_actions.validate_deploy_app(deploy_app)
        validation_actions.validate_deploy_app_dc_objects(deploy_app)

    def _prepare_deploy_app_result(
        self,
        deployed_vm: VmHandler,
        deploy_app: BaseVCenterDeployApp,
        vm_name: str,
    ) -> DeployAppResult:
        vm_details_data = self._prepare_vm_details_data(
            deployed_vm=deployed_vm,
            deploy_app=deploy_app,
        )

        self._logger.info(f"Prepared VM details: {vm_details_data}")

        return DeployAppResult(
            actionId=deploy_app.actionId,
            vmUuid=deployed_vm.uuid,
            vmName=vm_name,
            vmDetailsData=vm_details_data,
            deployedAppAdditionalData={
                "ip_regex": deploy_app.ip_regex,
                "refresh_ip_timeout": deploy_app.refresh_ip_timeout,
                "auto_power_off": deploy_app.auto_power_off,
                "auto_delete": deploy_app.auto_delete,
            },
        )

    def _get_vm_resource_pool(
        self, deploy_app: BaseVCenterDeployApp, dc: DcHandler
    ) -> ResourcePoolHandler | None:
        conf = self._resource_config
        self._logger.info("Getting VM resource pool")
        vm_resource_pool_name = deploy_app.vm_resource_pool or conf.vm_resource_pool
        vm_cluster_name = deploy_app.vm_cluster or conf.vm_cluster

        resource_pool = None
        if vm_resource_pool_name:
            self._logger.info(f"Getting resource pool by name: {vm_resource_pool_name}")
            resource_pool = dc.get_resource_pool(vm_resource_pool_name)
        elif vm_cluster_name:
            self._logger.info(
                f"Getting resource pool from the VM cluster: {vm_cluster_name}"
            )
            vm_cluster = dc.get_cluster(vm_cluster_name)
            resource_pool = vm_cluster.get_resource_pool()
        return resource_pool

    def _prepare_vm_folder_path(self, deploy_app: BaseVCenterDeployApp) -> VcenterPath:
        self._logger.info("Preparing VM folder")
        return get_vm_folder_path(
            deploy_app, self._resource_config, self._reservation_info.reservation_id
        )

    def _deploy(self, request_actions: DeployVMRequestActions) -> DeployAppResult:
        """Deploy VCenter VM."""
        conf = self._resource_config
        # noinspection PyTypeChecker
        deploy_app: BaseVCenterDeployApp = request_actions.deploy_app

        with self._cancellation_manager:
            self._validate_deploy_app(deploy_app)

        if deploy_app.autogenerated_name:
            vm_name = generate_name(deploy_app.app_name)
        else:
            vm_name = deploy_app.app_name

        self._logger.info(f"Generated name for the VM: {vm_name}")

        vm_folder_path = self._prepare_vm_folder_path(deploy_app)
        self._logger.info(f"Prepared folder for the VM: {vm_folder_path}")

        with self._cancellation_manager:
            self._logger.info(f"Getting Datacenter {conf.default_datacenter}")
            dc = DcHandler.get_dc(conf.default_datacenter, self._si)

        with self._cancellation_manager:
            vm_resource_pool = self._get_vm_resource_pool(deploy_app, dc)
        self._logger.info(f"Received VM resource pool: {vm_resource_pool}")

        with self._cancellation_manager:
            self._logger.info(f"Creating VM folders for path: {vm_folder_path}")
            vm_folder = dc.get_or_create_vm_folder(vm_folder_path)
            if self._vsphere_client is not None:
                self._vsphere_client.assign_tags(obj=vm_folder)

        with self._cancellation_manager:
            vm_storage_name = deploy_app.vm_storage or conf.vm_storage
            self._logger.info(f"Getting VM storage {vm_storage_name}")
            vm_storage = dc.get_datastore(vm_storage_name)

        with self._rollback_manager:
            self._logger.info(f"Creating VM {vm_name}")
            deployed_vm = self._create_vm(
                deploy_app=deploy_app,
                vm_name=vm_name,
                vm_resource_pool=vm_resource_pool,
                vm_storage=vm_storage,
                vm_folder=vm_folder,
                dc=dc,
            )

            if self._vsphere_client is not None:
                self._vsphere_client.assign_tags(obj=deployed_vm)

        self._logger.info(f"Preparing Deploy App result for the {deployed_vm}")
        return self._prepare_deploy_app_result(
            deployed_vm=deployed_vm,
            deploy_app=deploy_app,
            vm_name=vm_name,
        )


class AbstractVCenterDeployVMFromTemplateFlow(AbstractVCenterDeployVMFlow):
    @abstractmethod
    def _get_vm_template(
        self, deploy_app: BaseVCenterDeployApp, dc: DcHandler
    ) -> VmHandler:
        """Get VM template to clone VM from."""
        pass

    def _create_vm_customization_spec(
        self, deploy_app: BaseVCenterDeployApp, vm_template: VmHandler, vm_name: str
    ) -> CustomSpecHandler:
        custom_spec_params = get_custom_spec_params(deploy_app, vm_template)

        spec = None
        if deploy_app.customization_spec:
            if deploy_app.customization_spec != vm_name:
                self._si.duplicate_customization_spec(
                    deploy_app.customization_spec, vm_name
                )
            spec = self._si.get_customization_spec(vm_name)
        elif custom_spec_params:
            spec = create_custom_spec_from_spec_params(custom_spec_params, vm_name)

        if spec:
            num_of_nics = len(vm_template.vnics)
            if custom_spec_params:
                spec.set_custom_spec_params(custom_spec_params, num_of_nics)

            if deploy_app.customization_spec:
                self._si.overwrite_customization_spec(spec)
            else:
                self._si.create_customization_spec(spec)
        return spec

    def _get_vm_snapshot(
        self, deploy_app: BaseVCenterDeployApp, vm_template: VmHandler
    ) -> SnapshotHandler:
        """Get VM Snapshot to clone from."""
        pass

    def _create_vm(
        self,
        deploy_app: BaseVCenterDeployApp,
        vm_name: str,
        vm_resource_pool: ResourcePoolHandler,
        vm_storage: DatastoreHandler,
        vm_folder: FolderHandler,
        dc: DcHandler,
    ) -> VmHandler:
        """Create VM on the vCenter."""
        with self._cancellation_manager:
            vm_template = self._get_vm_template(deploy_app, dc)

        with self._cancellation_manager:
            # we create customization spec here and will set it on PowerOn command
            self._create_vm_customization_spec(deploy_app, vm_template, vm_name)

        with self._cancellation_manager:
            snapshot = self._get_vm_snapshot(deploy_app, vm_template)

        config_spec = ConfigSpecHandler.from_deploy_add(deploy_app)

        return CloneVMCommand(
            rollback_manager=self._rollback_manager,
            cancellation_manager=self._cancellation_manager,
            logger=self._logger,
            task_waiter=self._task_waiter,
            vm_template=vm_template,
            vm_name=vm_name,
            vm_resource_pool=vm_resource_pool,
            vm_storage=vm_storage,
            vm_folder=vm_folder,
            vm_snapshot=snapshot,
            config_spec=config_spec,
        ).execute()
