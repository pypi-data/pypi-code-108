import os
import warnings
from typing import Any, Dict, List, Optional, Union, Type

from nornir.core.inventory import ConnectionOptions
from nornir.core.inventory import Defaults
from nornir.core.inventory import Groups
from nornir.core.inventory import Host
from nornir.core.inventory import HostOrGroup
from nornir.core.inventory import Hosts
from nornir.core.inventory import Inventory

import requests

from rich import print


def _get_connection_options(data: Dict[str, Any]) -> Dict[str, ConnectionOptions]:
    """
	TODO: write docstrings
	"""

    cp = {}
    for cn, c in data.items():
        cp[cn] = ConnectionOptions(
            hostname=c.get("hostname"),
            port=c.get("port"),
            username=c.get("username"),
            password=c.get("password"),
            platform=c.get("platform"),
            extras=c.get("extras"),
        )
    return cp


def _get_inventory_element(
    typ: Type[HostOrGroup], data: Dict[str, Any], name: str, defaults: Defaults
) -> HostOrGroup:
    """
	TODO: write docstrings
	"""

    return typ(
        name=name,
        hostname=data.get("hostname"),
        port=data.get("port"),
        username=data.get("username"),
        password=data.get("password"),
        platform=data.get("platform"),
        data=data.get("data"),
        groups=data.get(
            "groups"
        ),  # this is a hack, we will convert it later to the correct type
        defaults=defaults,
        connection_options=_get_connection_options(
            data.get("connection_options", {})),
    )


class NetBoxInventory:
    """
    Inventory plugin that uses `NetBox <https://github.com/netbox-community/netbox>`_ as backend.
    Note:
        Additional data provided by the NetBox devices API endpoint will be
        available through the NetBox Host data attribute.
    Environment Variables:
        * ``NB_URL``: Corresponds to nb_url argument
        * ``NB_TOKEN``: Corresponds to nb_token argument
    Arguments:
        nb_url: NetBox url (defaults to ``http://localhost:8080``)
        nb_token: NetBox API token
        ssl_verify: Enable/disable certificate validation or provide path to CA bundle file
            (defaults to True)
        flatten_custom_fields: Assign custom fields directly to the host's data attribute
            (defaults to False)
        filter_parameters: Key-value pairs that allow you to filter the NetBox inventory.
        include_vms: Get virtual machines from NetBox as well as devices.
            (defaults to False)
        use_platform_slug: Use the NetBox platform slug for the platform attribute of a Host
            (defaults to False)
        use_platform_napalm_driver: Use the Netbox platform napalm driver setting for the
            platform attribute of a Host
            (defaults to False)
    """

    def __init__(
        self,
        nb_url: Optional[str] = None,
        nb_token: Optional[str] = None,
        ssl_verify: Union[bool, str] = True,
        flatten_custom_fields: bool = False,
        filter_parameters: Optional[Dict[str, Any]] = None,
        include_vms: bool = False,
        use_platform_slug: bool = False,
        use_platform_napalm_driver: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        TODO: write docstrings
        """
        filter_parameters = filter_parameters or {}
        nb_url = nb_url or os.environ.get("NB_URL", "http://localhost:8080")
        nb_token = nb_token or os.environ.get(
            "NB_TOKEN", "0123456789abcdef0123456789abcdef01234567"
        )

        self.nb_url = nb_url
        self.flatten_custom_fields = flatten_custom_fields
        self.filter_parameters = filter_parameters
        self.include_vms = include_vms
        self.use_platform_slug = use_platform_slug
        self.use_platform_napalm_driver = use_platform_napalm_driver

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {nb_token}"})
        self.session.verify = ssl_verify

        if self.use_platform_slug and self.use_platform_napalm_driver:
            raise ValueError(
                "Only one of use_platform_slug and use_platform_napalm_driver can be set to true"
            )

    def load(self) -> Inventory:
        """
        TODO: write docstrings
        """

        if self.use_platform_napalm_driver:
            platforms: List[Dict[str, Any]] = []
            platforms = self._get_resources(
                url=f"{self.nb_url}/api/dcim/platforms/?limit=0", params={}
            )

        nb_devices: List[Dict[str, Any]] = []

        nb_devices = self._get_devices_from_circuits(
            url=f"{self.nb_url}/api/circuits/circuits/?limits=0",
            params=self.filter_parameters,
        )

        if self.include_vms:
            nb_devices.extend(
                self._get_resources(
                    url=f"{self.nb_url}/api/virtualization/virtual-machines/?limit=0",
                    params=self.filter_parameters,
                )
            )

        hosts = Hosts()
        groups = Groups()
        defaults = Defaults()

        for device in nb_devices:
            serialized_device: Dict[Any, Any] = {}
            serialized_device["data"] = device

            if self.flatten_custom_fields:
                for cf, value in device["custom_fields"].items():
                    serialized_device["data"][cf] = value
                serialized_device["data"].pop("custom_fields")

            hostname = None
            if device.get("primary_ip"):
                hostname = device.get("primary_ip", {}).get(
                    "address", "").split("/")[0]
            else:
                if device.get("name") is not None:
                    hostname = device["name"]
            serialized_device["hostname"] = hostname

            if isinstance(device["platform"], dict) and self.use_platform_slug:
                platform = device["platform"].get("slug")
            elif (
                isinstance(device["platform"],
                           dict) and self.use_platform_napalm_driver
            ):
                platform = [
                    platform
                    for platform in platforms
                    if device["platform"]["slug"] == platform["slug"]
                ][0]["napalm_driver"]
            elif isinstance(device["platform"], dict):
                platform = device["platform"].get("name")
            else:
                platform = device["platform"]

            serialized_device["platform"] = platform

            name = serialized_device["data"].get("name") or str(
                serialized_device["data"].get("id")
            )

            hosts[name] = _get_inventory_element(
                Host, serialized_device, name, defaults
            )

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)

    def _get_resources(self, url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        TODO: write docstrings
        """

        resources: List[Dict[str, Any]] = []

        while url:
            r = self.session.get(url, params=params)

            if not r.status_code == 200:
                raise ValueError(
                    f"Failed to get data from NetBox instance {self.nb_url}. Status code: {r.status_code}"
                )

            resp = r.json()
            resources.extend(resp.get("results"))

            url = resp.get("next")
        return resources

    def _get_devices_from_circuits(self, url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        TODO: write docstrings
        """

        circuits: List[Dict[str, Any]] = []

        devices: List[Dict[str, Any]] = []
        devices_dict = {}

        while url:
            r = self.session.get(url, params=params)

            if not r.status_code == 200:
                raise ValueError(
                    f"Failed to get data from NetBox instance {self.nb_url}. Status code: {r.status_code}"
                )

            resp = r.json()
            circuits.extend(resp.get("results"))

            url = resp.get("next")

        for circuit in circuits:
            termination_a = self._get_resources(
                url=f"{self.nb_url}/api/circuits/circuit-terminations/", params={"id": circuit["termination_a"]["id"]})
            termination_z = self._get_resources(
                url=f"{self.nb_url}/api/circuits/circuit-terminations/", params={"id": circuit["termination_z"]["id"]})

            if termination_a:
                device_a = self._get_resources(
                    url=f"{self.nb_url}/api/dcim/devices", params={"id": termination_a[0]["cable_peer"]["device"]["id"]})
                if device_a:

                    if device_a[0]["name"] in devices_dict:
                        device = devices_dict.get(device_a[0]["name"])
                        device["tags"].append(circuit["status"]["value"])
                        devices_dict[device_a[0]["name"]] = device

                    else:
                        device_a[0]["tags"].append(
                            circuit["status"]["value"])
                        devices_dict[device_a[0]["name"]] = device_a[0]
            if termination_z:
                device_z = self._get_resources(
                    url=f"{self.nb_url}/api/dcim/devices", params={"id": termination_z[0]["cable_peer"]["device"]["id"]})
                if device_z:
                    devices_dict[device_z[0]["name"]] = device_z[0]
        devices = devices_dict.values()
        return devices
