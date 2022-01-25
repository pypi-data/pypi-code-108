from dataclasses import dataclass
import dataclasses
import os
import re
import requests
import sys


@dataclass
class AMDGPU:
    vendor_id: int
    product_id: int
    revision: int
    marketing_name: str

    # Fields initialized using the flags string
    flags: dataclasses.InitVar[str] = None
    is_APU: bool = None
    is_Mobility: bool = None
    has_experimental_support: bool = None

    def __post_init__(self, flags):
        for flag in [f.strip() for f in flags.split('|')]:
            if flag.startswith("CHIP_"):
                self.amdgpu_codename = flag[5:]
            elif flag == "AMD_IS_APU":
                self.is_APU = True
            elif flag == "AMD_IS_MOBILITY":
                self.is_Mobility = True
            elif flag == "AMD_EXP_HW_SUPPORT":
                self.has_experimental_support = True
            else:
                print(f"WARNING: Unknown flag '{flag}'")

        if self.architecture is None:
            print(f"{self.amdgpu_codename}: Unknown architecture", file=sys.stderr)
        if self.family is None:
            print(f"{self.amdgpu_codename}: Unknown family", file=sys.stderr)
        if self.gfx_version is None:
            print(f"{self.amdgpu_codename}: Unknown GFX version", file=sys.stderr)

    @property
    def codename(self):
        codenames = {
            "SIENNA_CICHLID": "NAVI21",
            "NAVY_FLOUNDER": "NAVI22",
            "DIMGREY_CAVEFISH": "NAVI23",
            "BEIGE_GOBY": "NAVI24",
            "YELLOW_CARP": "REMBRANDT",
        }

        return codenames.get(self.amdgpu_codename, self.amdgpu_codename)

    @property
    def family(self):
        families = {
            # SI
            "TAHITI": "SI",
            "PITCAIRN": "SI",
            "VERDE": "SI",
            "OLAND": "SI",
            "HAINAN": "SI",

            # CI
            "BONAIRE": "CI",
            "HAWAII": "CI",
            "KAVERI": "CI",

            # KV
            "KABINI": "KV",

            # VI
            "TONGA": "VI",
            "FIJI": "VI",
            "POLARIS10": "VI",
            "POLARIS11": "VI",
            "POLARIS12": "VI",
            "VEGAM": "VI",

            # CZ
            "CARRIZO": "CZ",
            "STONEY": "CZ",

            # AI
            "VEGA10": "AI",
            "VEGA12": "AI",
            "VEGA20": "AI",
            "ARCTURUS": "AI",

            # RV
            "RAVEN": "RV",
            "RENOIR": "RV",

            # NV
            "NAVI10": "NV",
            "NAVI12": "NV",
            "NAVI14": "NV",

            # Unknowns
            "MULLINS": "UNK",
            "TOPAZ": "UNK",
            "CYAN_SKILLFISH": "UNK",
            "NAVI21": "UNK",
            "VANGOGH": "UNK",
            "NAVI22": "UNK",
            "NAVI23": "UNK",
            "NAVI24": "UNK",
            "REMBRANDT": "UNK",
            "ALDEBARAN": "UNK",
        }

        return families.get(self.codename)

    @property
    def architecture(self):
        architectures = {
            # GCN1
            "TAHITI": "GCN1",
            "PITCAIRN": "GCN1",
            "VERDE": "GCN1",
            "OLAND": "GCN1",
            "HAINAN": "GCN1",

            # GCN2
            "KAVERI": "GCN2",
            "BONAIRE": "GCN2",
            "HAWAII": "GCN2",
            "KABINI": "GCN2",
            "MULLINS": "GCN2",

            # GCN3
            "TOPAZ": "GCN3",
            "TONGA": "GCN3",
            "FIJI": "GCN3",
            "CARRIZO": "GCN3",
            "STONEY": "GCN3",

            # GCN4
            "POLARIS10": "GCN4",
            "POLARIS11": "GCN4",
            "POLARIS12": "GCN4",
            "VEGAM": "GCN4",

            # GCN5
            "VEGA10": "GCN5",
            "VEGA12": "GCN5",
            "RAVEN": "GCN5",

            # GCN5.1
            "VEGA20": "GCN5.1",
            "RENOIR": "GCN5.1",

            # CDNA
            "ARCTURUS": "CDNA",

            # CDNA2
            "ALDEBARAN": "CDNA2",

            # Navi / RDNA1
            "NAVI10": "RDNA1",
            "NAVI12": "RDNA1",
            "NAVI14": "RDNA1",
            "CYAN_SKILLFISH": "RDNA1",

            # RDNA2
            "NAVI21": "RDNA2",
            "NAVI22": "RDNA2",
            "NAVI23": "RDNA2",
            "NAVI24": "RDNA2",
            "VANGOGH": "RDNA2",
            "REMBRANDT": "RDNA2",
        }

        return architectures.get(self.codename)

    @property
    def base_name(self):
        return self.gfx_version

    @property
    def gfx_version(self):
        versions = {
            # GFX7
            "GCN1": "gfx6",

            # GFX7
            "GCN2": "gfx7",

            # GFX8
            "GCN3": "gfx8",
            "GCN4": "gfx8",

            # GFX9
            "GCN5": "gfx9",
            "GCN5.1": "gfx9",
            "CDNA": "gfx9",
            "CDNA2": "gfx9",

            # GFX10
            "RDNA1": "gfx10",
            "RDNA2": "gfx10",
        }

        return versions.get(self.architecture)

    @property
    def tags(self):
        tags = set()

        tags.add(f"amdgpu:pciid:{self.pciid}")
        tags.add(f"amdgpu:family:{self.family}")
        tags.add(f"amdgpu:codename:{self.codename}")
        tags.add(f"amdgpu:architecture:{self.architecture}")
        tags.add(f"amdgpu:gfxversion:{self.gfx_version}")
        if self.is_APU:
            tags.add("amdgpu:APU")
        if self.has_experimental_support:
            tags.add("amdgpu:EXP_HW_SUPPORT")

        return tags

    @property
    def structured_tags(self):
        return {
            "type": "amdgpu",
            "pciid": self.pciid,
            "family": self.family,
            "codename": self.codename,
            "architecture": self.architecture,
            "gfxversion": self.gfx_version,
            "marketing_name": self.marketing_name,
            "APU": self.is_APU,
            "EXP_HW_SUPPORT": self.has_experimental_support
        }

    @property
    def pciid(self):
        return f"{hex(self.vendor_id)}:{hex(self.product_id)}"

    def __str__(self):
        return (f"<AMDGPU: PCIID {self.pciid} - {self.codename} - {self.family} - "
                f"{self.architecture} - {self.gfx_version.lower()}>")

    def __repr__(self):
        return f"{self.__class__}({self.__dict__})"


@dataclass
class AmdGpuDrvDev:
    vendor_id: int
    product_id: int
    flags: str

    @classmethod
    def generate_key(cls, vendor_id, product_id):
        return vendor_id << 16 | product_id

    @property
    def key(self):
        return self.generate_key(self.vendor_id, self.product_id)


@dataclass
class AmdGpuId:
    product_id: int
    revision: int
    marketing_name: str

    @classmethod
    def generate_key(cls, product_id, revision):
        return (product_id, revision)

    @property
    def key(self):
        return self.generate_key(self.product_id, self.revision)


class AmdGpuDeviceDB:
    # WARNING: Don't forget to update .gitlab-ci.yml when changing these URLs
    AMDGPU_DRV_URL = ("https://gitlab.freedesktop.org/agd5f/linux/-/raw/amd-staging-drm-next/"
                      "drivers/gpu/drm/amd/amdgpu/amdgpu_drv.c")
    AMDGPU_DRV_FILENAME = "amdgpu_drv.c"

    MARKETING_NAMES_URL = "https://gitlab.freedesktop.org/mesa/drm/-/raw/master/data/amdgpu.ids"
    MARKETING_NAMES_FILENAME = "amdgpu.ids"

    def __init__(self):
        self.is_up_to_date = False
        self.amdgpu_drv_devs = dict()
        self.amdgpu_ids_devs = dict()

        try:
            amdgpu_drv = open(self.amdgpu_drv_cache_path, 'r').read()
        except FileNotFoundError:
            amdgpu_drv = ""
        self._parse_amdgpu_drv(amdgpu_drv)

        try:
            amdgpu_ids = open(self.amdgpu_ids_cache_path, 'r').read()
        except FileNotFoundError:
            amdgpu_ids = ""

        self._parse_amdgpu_ids(amdgpu_ids)

    @property
    def amdgpu_drv_cache_path(self):
        package_directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(package_directory, self.AMDGPU_DRV_FILENAME)

    @property
    def amdgpu_ids_cache_path(self):
        package_directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(package_directory, self.MARKETING_NAMES_FILENAME)

    def _parse_amdgpu_drv(self, drv):
        self.amdgpu_drv_devs = dict()

        comp_re = re.compile(
            r"^\s*{(?P<vendor_id>0x[\da-fA-F]+),\s*(?P<product_id>0x[\da-fA-F]+),"
            r"\s*PCI_ANY_ID,\s*PCI_ANY_ID,\s*0,\s*0,\s*(?P<flags>.*)},\s*$")

        started = False
        for line in drv.splitlines():
            if not started:
                if line == "static const struct pci_device_id pciidlist[] = {":
                    started = True
                    continue
            else:
                if line == "	{0, 0, 0}":
                    break

                if m := comp_re.match(line):
                    try:
                        dev = AmdGpuDrvDev(vendor_id=int(m.group('vendor_id'), 0),
                                           product_id=int(m.group('product_id'), 0),
                                           flags=m.group('flags') or None)
                        self.amdgpu_drv_devs[dev.key] = dev
                    except ValueError:
                        continue

    def _parse_amdgpu_ids(self, ids):
        if ids is None:
            return None

        self.amdgpu_ids_devs = dict()
        for line in ids.splitlines():
            fields = line.split(',\t')
            if len(fields) == 3:
                try:
                    dev = AmdGpuId(product_id=int(fields[0], 16),
                                   revision=int(fields[1], 16),
                                   marketing_name=fields[2])
                    self.amdgpu_ids_devs[dev.key] = dev
                except ValueError:
                    pass

    def cache_db(self):
        r = requests.get(self.AMDGPU_DRV_URL, timeout=5)
        r.raise_for_status()
        open(self.amdgpu_drv_cache_path, "w").write(r.text)

        r = requests.get(self.MARKETING_NAMES_URL, timeout=5)
        r.raise_for_status()
        open(self.amdgpu_ids_cache_path, "w").write(r.text)

    def update(self):
        if self.is_up_to_date:
            return

        r = requests.get(self.AMDGPU_DRV_URL, timeout=5)
        r.raise_for_status()
        self._parse_amdgpu_drv(r.text)

        r = requests.get(self.MARKETING_NAMES_URL, timeout=5)
        r.raise_for_status()
        self._parse_amdgpu_ids(r.text)

        self.is_up_to_date = True

    @classmethod
    def host_cpu_name(cls):
        for line in open("/proc/cpuinfo").readlines():
            fields = line.split(":")
            if fields[0].strip() == "model name":
                return fields[1].strip()

        return None

    def from_pciid(self, vendor_id, product_id, revision):
        if amdgpu_dev := self.amdgpu_drv_devs.get(AmdGpuDrvDev.generate_key(vendor_id, product_id)):
            amdgpu_ids = self.amdgpu_ids_devs.get(AmdGpuId.generate_key(product_id, revision))
            marketing_name = amdgpu_ids.marketing_name if amdgpu_ids else None

            gpu = AMDGPU(vendor_id=vendor_id, product_id=product_id,
                         revision=revision, marketing_name=marketing_name,
                         flags=amdgpu_dev.flags)

            if gpu.marketing_name is None and gpu.is_APU:
                gpu.marketing_name = self.host_cpu_name()

            return gpu
