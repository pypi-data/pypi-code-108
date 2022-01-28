import re
from requests import get
from pprint import pprint
from typing import Callable

VALID_ARCHITECTURES = frozenset(["amd64", "i586", "i686", "armhf", "aarch64"])

commasep = lambda x: ", ".join(x)


class Distro:
    __slots__ = ("name", "_version", "_data", "_f")

    def __init__(self, f: Callable):
        self._f = f
        self._data = None
        self.name = f.__name__.replace("_", "-")

        DISTROS.update({self.name: self})

    @property
    def architectures(self) -> list[str]:
        self._assure_urls()
        return [i for i in self._data.keys() if i != "version"]

    @property
    def version(self) -> str:
        self._assure_urls()
        return self._version

    def _assure_urls(self) -> None:
        if self._data is None:
            # data structure: {
            #   version
            #   architectur (e.g. x86_64): {
            #       ?url
            #       ?torrent (url to torrent file)
            #       ?magnet
            #       ?hash (e.g. sha256)
            #   }
            # }
            data: dict = self._f()
            # verify data structure
            if not "version" in data:  # verison is required
                raise ValueError("missing version")
            self._version = data.pop("version")
            # replace x86_64 with amd64
            if "x86_64" in data:
                data["amd64"] = data.pop("x86_64")
            # verify the architectures
            if invalid := set(data.keys()) - VALID_ARCHITECTURES:
                raise ValueError(f"invalid architecture: {commasep(invalid)}")
            # verify data structure for each architecture
            for arch_name, arch_data in data.items():
                if invalid := set(arch_data.keys()) - {"url", "magnet", "torrent", "md5", "sha256", "sha1"}:
                    raise ValueError(f"invalid keys for architecture {arch_name}: {commasep(invalid)}")
                # if a key is set to None, remove it
                for key in [*arch_data.keys()]:
                    if arch_data[key] is None:
                        arch_data.pop(key)

            self._data = data

    def __getitem__(self, key: str) -> dict[str, str]:
        self._assure_urls()
        if key == "x86_64":
            key = "amd64"
        if not key in self._data.keys():
            raise KeyError(
                f"No ISO available for architecture {key}. Valid architectures: {commasep(self.architectures)}"
            )
        return self._data[key]

    def __repr__(self) -> str:
        return f"Distro('{self.name}')"


DISTROS: Distro = {}


# archlinux
@Distro
def archlinux():  # as of January 2022
    baseurl = "https://archlinux.org"
    data = get(f"{baseurl}/releng/releases/json").json()["releases"][0]
    version = data["version"]
    return {
        "version": version,
        "amd64": {
            "url": f"https://mirror.rackspace.com/archlinux{data['iso_url']}",  # official worldwide mirror
            "torrent": f"{baseurl}{data['torrent_url']}",
            "magnet": data["magnet_uri"],
            "md5": data["md5_sum"],
            "sha256": data["sha256_sum"],
            "sha1": data["sha1_sum"],
        },
    }


# Debian
@Distro
def debian():  # as of January 2022
    baseurl = "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/"
    data = get(f"{baseurl}/SHA256SUMS")
    print(data.text)
    sha256, version = re.search(r"^([a-f0-9]*)\s*debian-(.*)-amd64-netinst.iso$", data.text, re.M | re.I).groups()
    return {
        "version": version,
        "amd64": {
            "url": f"{baseurl}/debian-{version}-amd64-netinst.iso",
            "sha256": sha256,
        },
    }


pprint([*DISTROS])
# pprint(DISTROS["archlinux"]["amd64"])
