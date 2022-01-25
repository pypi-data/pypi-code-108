from .amdgpu import AmdGpuDeviceDB
from .intel import IntelGpuDeviceDB
from .virt import VirtIOGpuDeviceDB
from .gfxinfo_vulkan import VulkanInfo


SUPPORTED_GPU_DBS = [AmdGpuDeviceDB(), IntelGpuDeviceDB(), VirtIOGpuDeviceDB()]


def pci_devices():
    devices = open('/proc/bus/pci/devices').readlines()
    ids = [line.split('\t')[1:3] for line in devices]
    return [(int(id[:4], 16), int(id[4:], 16), int(rev, 16)) for id, rev in ids]


def find_gpu():
    """For now we only support single-gpu DUTs"""
    devices = pci_devices()

    for pci_device in devices:
        for gpu_db in SUPPORTED_GPU_DBS:
            if gpu := gpu_db.from_pciid(*pci_device):
                return gpu

    # We could not find the GPU in our databases, update them
    for gpu_db in SUPPORTED_GPU_DBS:
        gpu_db.update()

    # Retry, now that we have updated our DBs
    for pci_device in devices:
        for gpu_db in SUPPORTED_GPU_DBS:
            if gpu := gpu_db.from_pciid(*pci_device):
                return gpu


def cache_db():
    for gpu_db in SUPPORTED_GPU_DBS:
        gpu_db.cache_db()


__all__ = ['pci_devices', 'find_gpu', 'cache_db', 'VulkanInfo']
