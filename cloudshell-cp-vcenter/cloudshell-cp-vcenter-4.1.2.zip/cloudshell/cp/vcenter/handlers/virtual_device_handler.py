import attr
from pyVmomi import vim


def is_vnic(device) -> bool:
    return isinstance(device, vim.vm.device.VirtualEthernetCard)


def is_virtual_disk(device) -> bool:
    return isinstance(device, vim.vm.device.VirtualDisk)


def is_virtual_scsi_controller(device) -> bool:
    return isinstance(device, vim.vm.device.VirtualSCSIController)


@attr.s(auto_attribs=True)
class VirtualDeviceHandler:
    _device: vim.vm.device.VirtualDevice

    @property
    def label(self) -> str:
        return self._device.deviceInfo.label
