from __future__ import annotations

import os
from typing import TYPE_CHECKING, Iterable
from urllib.request import urlopen

import attr

from cloudshell.cp.vcenter.exceptions import (
    BaseVCenterException,
    InvalidAttributeException,
)
from cloudshell.cp.vcenter.handlers.cluster_handler import ClusterHandler
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.switch_handler import (
    DvSwitchNotFound,
    VSwitchNotFound,
)
from cloudshell.cp.vcenter.models.deploy_app import (
    BaseVCenterDeployApp,
    VMFromImageDeployApp,
    VMFromLinkedCloneDeployApp,
    VMFromTemplateDeployApp,
    VMFromVMDeployApp,
)

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


class SwitchNotFound(BaseVCenterException):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Neither dvSwitch nor vSwitch with name {name} not found")


# todo move this validation to the model
BEHAVIOURS_DURING_SAVE = ("Remain Powered On", "Power Off")


@attr.s(auto_attribs=True)
class ValidationActions:
    _si: SiHandler
    _resource_conf: VCenterResourceConfig
    _logger: Logger

    def _get_dc(self) -> DcHandler:
        return DcHandler.get_dc(self._resource_conf.default_datacenter, self._si)

    def validate_resource_conf(self):
        self._logger.info("Validating resource config")
        conf = self._resource_conf
        _is_not_empty(conf.address, "address")
        _is_not_empty(conf.user, conf.ATTR_NAMES.user)
        _is_not_empty(conf.password, conf.ATTR_NAMES.password)
        _is_not_empty(conf.default_datacenter, conf.ATTR_NAMES.default_datacenter)
        _is_not_empty(conf.vm_location, conf.ATTR_NAMES.vm_location)
        _is_value_in(
            conf.behavior_during_save,
            BEHAVIOURS_DURING_SAVE,
            conf.ATTR_NAMES.behavior_during_save,
        )

    def validate_resource_conf_dc_objects(self):
        self._logger.info("Validating resource config objects on the vCenter")
        conf = self._resource_conf
        dc = self._get_dc()
        dc.get_network(conf.holding_network)
        cluster = None
        if conf.vm_location:
            dc.get_vm_folder(conf.vm_location)
        if conf.vm_cluster:
            cluster = dc.get_cluster(conf.vm_cluster)
        if conf.vm_storage:
            dc.get_datastore(conf.vm_storage)
        if conf.saved_sandbox_storage:
            dc.get_datastore(conf.saved_sandbox_storage)
        if conf.default_dv_switch:
            self._validate_switch(dc, cluster)
        if conf.vm_resource_pool:
            dc.get_resource_pool(conf.vm_resource_pool)

    def validate_deploy_app_dc_objects(self, deploy_app):
        self._logger.info("Validating deploy app objects on the vCenter")
        self.validate_base_app_dc_objects(
            deploy_app.vm_location, deploy_app.vm_cluster, deploy_app.vm_storage
        )

    def validate_base_app_dc_objects(
        self, vm_location: str | None, vm_cluster: str | None, vm_storage: str | None
    ):
        dc = DcHandler.get_dc(self._resource_conf.default_datacenter, self._si)
        if vm_location:
            dc.get_vm_folder(vm_location)
        if vm_cluster:
            dc.get_cluster(vm_cluster)
        if vm_storage:
            dc.get_datastore(vm_storage)

    def validate_deploy_app(self, deploy_app: BaseVCenterDeployApp):
        self._logger.info("Validating deploy app")

        self.validate_base_app_attrs(
            deploy_app.vm_cluster, deploy_app.vm_storage, deploy_app.vm_location
        )

    def validate_base_app_attrs(
        self, vm_cluster: str | None, vm_storage: str | None, vm_location: str | None
    ):
        conf = self._resource_conf
        _one_is_not_empty([vm_cluster, conf.vm_cluster], conf.ATTR_NAMES.vm_cluster)
        _one_is_not_empty([vm_storage, conf.vm_storage], conf.ATTR_NAMES.vm_storage)
        _one_is_not_empty([vm_location, conf.vm_location], conf.ATTR_NAMES.vm_location)

    def validate_deploy_app_from_vm(self, deploy_app: VMFromVMDeployApp):
        self._logger.info("Validating deploy app from VM")
        self.validate_app_from_vm(deploy_app.vcenter_vm)

    def validate_app_from_vm(self, vm_path: str):
        _is_not_empty(vm_path, VMFromVMDeployApp.ATTR_NAMES.vcenter_vm)
        dc = self._get_dc()
        dc.get_vm_by_path(vm_path)

    def validate_deploy_app_from_template(self, deploy_app: VMFromTemplateDeployApp):
        self._logger.info("Validating deploy app from Template")
        self.validate_app_from_template(deploy_app.vcenter_template)

    def validate_app_from_template(self, vm_path: str):
        _is_not_empty(vm_path, VMFromTemplateDeployApp.ATTR_NAMES.vcenter_template)
        dc = self._get_dc()
        dc.get_vm_by_path(vm_path)

    def validate_deploy_app_from_clone(self, deploy_app: VMFromLinkedCloneDeployApp):
        self._logger.info("Validating deploy app from Linked Clone")
        self.validate_app_from_clone(
            deploy_app.vcenter_vm, deploy_app.vcenter_vm_snapshot
        )

    def validate_app_from_clone(self, vm_path: str, snapshot_path: str):
        _is_not_empty(vm_path, VMFromLinkedCloneDeployApp.ATTR_NAMES.vcenter_vm)
        _is_not_empty(
            snapshot_path, VMFromLinkedCloneDeployApp.ATTR_NAMES.vcenter_vm_snapshot
        )
        dc = self._get_dc()
        vm = dc.get_vm_by_path(vm_path)
        vm.get_snapshot_by_path(snapshot_path)

    def validate_deploy_app_from_image(self, deploy_app: VMFromImageDeployApp):
        self._logger.info("Validating deploy app from Image")
        self.validate_app_from_image(deploy_app.vcenter_image)

    def validate_app_from_image(self, image_url: str):
        _is_not_empty(image_url, VMFromImageDeployApp.ATTR_NAMES.vcenter_image)
        _is_valid_url(image_url, VMFromImageDeployApp.ATTR_NAMES.vcenter_image)

    def validate_ovf_tool(self, ovf_tool_path):
        self._logger.info("Validating OVF Tool")
        _is_not_empty(ovf_tool_path, self._resource_conf.ATTR_NAMES.ovf_tool_path)
        _is_valid_url(ovf_tool_path, self._resource_conf.ATTR_NAMES.ovf_tool_path)

    def _validate_switch(self, dc: DcHandler, cluster: ClusterHandler | None):
        switch_name = self._resource_conf.default_dv_switch
        try:
            dc.get_dv_switch(switch_name)
        except DvSwitchNotFound:
            if not cluster:
                raise SwitchNotFound(switch_name)
            try:
                cluster.get_v_switch(switch_name)
            except VSwitchNotFound:
                raise SwitchNotFound(switch_name)


def _is_valid_url(url: str, attr_name: str):
    try:
        urlopen(url)
    except Exception:
        if os.path.isfile(url):
            return True
    else:
        return True

    raise InvalidAttributeException(f"{attr_name} is invalid. Unable to access {url}")


def _is_not_empty(value: str, attr_name: str):
    if not value:
        raise InvalidAttributeException(f"{attr_name} cannot be empty")


def _is_value_in(value: str, expected_values: Iterable[str], attr_name: str):
    if value not in expected_values:
        raise InvalidAttributeException(
            f"{attr_name} should be one of the {list(expected_values)}"
        )


def _one_is_not_empty(values: list, attr_name: str):
    if not any(values):
        raise InvalidAttributeException(f"{attr_name} cannot be empty")
