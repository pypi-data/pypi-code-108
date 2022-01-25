from dataclasses import dataclass


@dataclass
class VirtGPU:
    vendor_id: int
    product_id: int
    revision: int

    @property
    def base_name(self):
        return 'virtio'

    @property
    def pciid(self):
        return f"{hex(self.vendor_id)}:{hex(self.product_id)}"

    @property
    def tags(self):
        return {
            f"virtio:pciid:{self.pciid}",
            "virtio:family:VIRTIO",
        }

    @property
    def structured_tags(self):
        return {
            "type": "virtio"
        }

    def __str__(self):
        return f"<VirtGPU: PCIID {self.pciid}>"


class VirtIOGpuDeviceDB:
    def cache_db(self):
        # NOTHING TO DO
        pass

    def update(self):
        # NOTHING TO DO
        pass

    def from_pciid(self, vendor_id, product_id, revision):
        if vendor_id != 0x1af4 and product_id != 0x1050:
            return None
        else:
            return VirtGPU(vendor_id=vendor_id, product_id=product_id, revision=revision,)
