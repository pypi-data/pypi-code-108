from cloudshell.cp.vcenter.handlers.virtual_device_handler import VirtualDeviceHandler


class VirtualDiskHandler(VirtualDeviceHandler):
    @property
    def capacity_in_bytes(self) -> int:
        return self._device.capacityInBytes
