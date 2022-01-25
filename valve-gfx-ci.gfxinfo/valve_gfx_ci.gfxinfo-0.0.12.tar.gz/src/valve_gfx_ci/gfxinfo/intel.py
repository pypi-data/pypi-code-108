from dataclasses import dataclass


@dataclass
class IntelGPU:
    vendor_id: int
    product_id: int
    revision: int
    gen_version: int
    family: str

    @property
    def base_name(self):
        return 'intel' + self.gen_version

    @property
    def pciid(self):
        return f"{hex(self.vendor_id)}:{hex(self.product_id)}"

    @property
    def tags(self):
        return {
            f"intelgpu:pciid:{self.pciid}",
            f"intelgpu:family:{self.family}",
            f"intelgpu:gen:{self.gen_version}",
        }

    @property
    def structured_tags(self):
        return {
            "type": "intelgpu",
            "family": self.family,
            "gen": self.gen_version
        }

    def __str__(self):
        return f"<IntelGPU: PCIID {self.pciid} - gen{self.gen_version} - {self.family}>"


class IntelGpuDeviceDB:
    def cache_db(self):
        # NOTHING TO DO
        pass

    def update(self):
        # NOTHING TO DO
        pass

    def from_pciid(self, vendor_id, product_id, revision):
        if vendor_id != 0x8086:
            return None

        SUPPORTED_GPUS = {
            0x3e9b: {
                'gen_version': '9',
                'family': 'COFFEELAKE'
            },
        }
        if md := SUPPORTED_GPUS.get(product_id):
            return IntelGPU(vendor_id=vendor_id, product_id=product_id, revision=revision, **md)
