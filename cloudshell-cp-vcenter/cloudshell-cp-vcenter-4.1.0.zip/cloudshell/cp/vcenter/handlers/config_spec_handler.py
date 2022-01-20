from __future__ import annotations

import re
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

import attr
from pyVmomi import vim

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.models.base_deployment_app import HddSpec
from cloudshell.cp.vcenter.utils.vm_helpers import (
    get_all_devices,
    get_device_key,
    get_virtual_disks,
    get_virtual_scsi_controllers,
)

if TYPE_CHECKING:
    from cloudshell.cp.vcenter.models.deploy_app import BaseVCenterDeployApp


MAX_NUMBER_OF_VM_DISKS = 16
SCSI_CONTROLLER_UNIT_NUMBER = 7


class ReconfigureVMError(BaseVCenterException):
    ...


class MaxDiskNumberExceedError(ReconfigureVMError):
    def __init__(self):
        super().__init__(
            f"Unable to create a new disk device. {MAX_NUMBER_OF_VM_DISKS} disks "
            f"limit has been exceeded"
        )


class HddReduceSizeError(ReconfigureVMError):
    def __init__(self, hdd_spec: HddSpec, current_size_in_kb: int):
        self.hdd_spec = hdd_spec
        self.current_size_in_kb = current_size_in_kb
        super().__init__(
            f"Invalid new size of 'Hard disk {hdd_spec.num}'. Current disk size "
            f"{current_size_in_kb}KB cannot be reduced to {hdd_spec.size_in_kb}KB"
        )


class InvalidDiskNumber(ReconfigureVMError):
    def __init__(self, disk_num: int, expected_disk_num: int):
        self.disk_num = disk_num
        self.expected_disk_num = expected_disk_num
        super().__init__(
            f"Invalid new hard disk number '{disk_num}'."
            f" Disk must have name 'Hard disk {expected_disk_num}'"
        )


class UnableToFindScsiController(ReconfigureVMError):
    def __init__(self):
        super().__init__("Unable to find Controller for the new VM Disk creation")


def _get_disk_num(name: str) -> int:
    return int(re.search(r"\d+", name).group())


def _yield_device_unit_number(vm: vim.VirtualMachine) -> Generator[int, None, None]:
    """Get generator for the next available device unit number."""
    unit_numbers = list(range(MAX_NUMBER_OF_VM_DISKS))
    unit_numbers.remove(SCSI_CONTROLLER_UNIT_NUMBER)

    for dev in get_all_devices(vm):
        if hasattr(dev.backing, "fileName") and dev.unitNumber in unit_numbers:
            unit_numbers.remove(dev.unitNumber)

    yield from unit_numbers

    raise MaxDiskNumberExceedError()


def _yield_disk_device_key(vm: vim.VirtualMachine) -> Generator[int, None, None]:
    """Get generator for the next available disk key number."""
    all_devices_keys = set(map(get_device_key, get_all_devices(vm)))
    last_disk_key = max(map(get_device_key, get_virtual_disks(vm)))

    while True:
        last_disk_key += 1
        if last_disk_key not in all_devices_keys:
            yield last_disk_key


@attr.s(auto_attribs=True)
class ConfigSpecHandler:
    cpu_num: int | None
    ram_amount: float | None
    hdd_specs: list[HddSpec]

    def __bool__(self) -> bool:
        return bool(self.cpu_num or self.ram_amount or self.hdd_specs)

    @classmethod
    def from_deploy_add(cls, deploy_app: BaseVCenterDeployApp) -> ConfigSpecHandler:
        return cls(
            deploy_app.cpu_num,
            deploy_app.ram_amount,
            deploy_app.hdd_specs,
        )

    @classmethod
    def from_strings(
        cls, cpu: str | None, ram: str | None, hdd: str | None
    ) -> ConfigSpecHandler:
        return cls(
            int(cpu) if cpu else None,
            float(ram) if ram else None,
            list(map(HddSpec.from_str, hdd.split(";"))) if hdd else [],
        )

    def _update_hdd_specs(self, config_spec, vm: vim.VirtualMachine):
        existing_disks = {
            _get_disk_num(disk.deviceInfo.label): disk for disk in get_virtual_disks(vm)
        }
        last_disk_number = max(existing_disks.keys(), default=0)
        unit_number_gen = _yield_device_unit_number(vm)
        dev_key_gen = _yield_disk_device_key(vm)

        # noinspection PyTypeChecker
        for hdd_spec in sorted(self.hdd_specs):
            disk = existing_disks.get(hdd_spec.num)
            if disk:
                disk_spec = self._create_update_hdd_spec(disk, hdd_spec)
            else:
                last_disk_number += 1
                if hdd_spec.num != last_disk_number:
                    raise InvalidDiskNumber(hdd_spec.num, last_disk_number)
                disk_spec = self._create_new_hdd_spec(
                    hdd_spec, dev_key_gen, unit_number_gen, vm
                )
            if disk_spec:
                config_spec.deviceChange.append(disk_spec)

    @staticmethod
    def _create_update_hdd_spec(
        disk, hdd_spec: HddSpec
    ) -> vim.vm.device.VirtualDeviceSpec | None:
        if disk.capacityInKB == hdd_spec.size_in_kb:
            disk_spec = None
        elif disk.capacityInKB > hdd_spec.size_in_kb:
            raise HddReduceSizeError(hdd_spec, disk.capacityInKB)
        else:
            disk.capacityInKB = hdd_spec.size_in_kb
            disk_spec = vim.vm.device.VirtualDeviceSpec(
                device=disk,
                operation=vim.vm.device.VirtualDeviceSpec.Operation.edit,
            )
        return disk_spec

    def _create_new_hdd_spec(
        self,
        hdd_spec: HddSpec,
        dev_key_gen: Iterator[int],
        unit_number_gen: Iterator[int],
        vm: vim.VirtualMachine,
    ) -> vim.vm.device.VirtualDeviceSpec:
        new_disk = vim.vm.device.VirtualDisk()
        new_disk.key = next(dev_key_gen)
        new_disk.controllerKey = self._get_device_controller_key(vm)
        new_disk.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        new_disk.backing.diskMode = "persistent"
        new_disk.unitNumber = next(unit_number_gen)
        new_disk.capacityInKB = hdd_spec.size_in_kb

        disk_spec = vim.vm.device.VirtualDeviceSpec(
            fileOperation=vim.vm.device.VirtualDeviceSpec.FileOperation.create,
            operation=vim.vm.device.VirtualDeviceSpec.Operation.add,
            device=new_disk,
        )
        return disk_spec

    @staticmethod
    def _get_device_controller_key(vm: vim.VirtualMachine):
        try:
            key = next(map(get_device_key, get_virtual_scsi_controllers(vm)))
        except StopIteration:
            raise UnableToFindScsiController()
        return key

    def get_spec_for_vm(self, vm: vim.VirtualMachine) -> vim.vm.ConfigSpec:
        config_spec = vim.vm.ConfigSpec(
            cpuHotAddEnabled=True, cpuHotRemoveEnabled=True, memoryHotAddEnabled=True
        )
        if self.cpu_num is not None:
            config_spec.numCPUs = self.cpu_num
        if self.ram_amount is not None:
            config_spec.memoryMB = int(self.ram_amount * 1024)
        if self.hdd_specs:
            self._update_hdd_specs(config_spec, vm)
        return config_spec
