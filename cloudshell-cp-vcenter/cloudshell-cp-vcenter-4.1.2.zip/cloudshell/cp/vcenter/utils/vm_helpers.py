from __future__ import annotations

from typing import Iterator

from pyVmomi import vim

from cloudshell.cp.vcenter.constants import DEPLOYED_APPS_FOLDER
from cloudshell.cp.vcenter.handlers.vcenter_path import VcenterPath
from cloudshell.cp.vcenter.models.deploy_app import BaseVCenterDeployApp
from cloudshell.cp.vcenter.models.deployed_app import BaseVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


def is_vnic(device) -> bool:
    return isinstance(device, vim.vm.device.VirtualEthernetCard)


def is_virtual_disk(device) -> bool:
    return isinstance(device, vim.vm.device.VirtualDisk)


def is_virtual_scsi_controller(device) -> bool:
    return isinstance(device, vim.vm.device.VirtualSCSIController)


def get_device_key(device):
    return device.key


def get_all_devices(vm: vim.VirtualMachine):
    return vm.config.hardware.device


def get_vnics(vm: vim.VirtualMachine) -> Iterator[vim.vm.device.VirtualEthernetCard]:
    return filter(is_vnic, get_all_devices(vm))


def get_virtual_disks(vm: vim.VirtualMachine) -> Iterator[vim.vm.device.VirtualDisk]:
    return filter(is_virtual_disk, get_all_devices(vm))


def get_virtual_scsi_controllers(
    vm: vim.VirtualMachine,
) -> Iterator[vim.vm.device.VirtualSCSIController]:
    return filter(is_virtual_scsi_controller, get_all_devices(vm))


def get_vm_folder_path(
    model: BaseVCenterDeployApp | BaseVCenterDeployedApp,
    resource_conf: VCenterResourceConfig,
    reservation_id: str,
) -> VcenterPath:
    path = VcenterPath(model.vm_cluster or resource_conf.vm_location)
    path.append(DEPLOYED_APPS_FOLDER)
    path.append(reservation_id)
    return path
