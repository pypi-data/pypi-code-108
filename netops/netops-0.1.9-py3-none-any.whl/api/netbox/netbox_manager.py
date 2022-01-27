from nornir import InitNornir
from nornir.core.inventory import Host
from . inventory_plugin import NetBoxInventory
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir.core.plugins.inventory import TransformFunctionRegister
from nornir.core.exceptions import (
    PluginAlreadyRegistered
)
import pynetbox
import requests
import os


NB_PRIVATE_KEY = os.environ.get("NB_PRIVATE_KEY")
CONTEXT = os.environ.get("CI_COMMIT_REF_NAME")
NB_URL = os.environ.get("NB_URL")
NB_TOKEN = os.environ.get("NB_TOKEN")


class NetboxManager:
    """
    NetboxManager manages the object that hosts infrastruxture data from NetBox host.
    
    TODO: write docstrings
    ...

    Attributes
    ----------
    filter_params : str
        ...
    

    Methods
    -------
    inject_host_data_validation(host)
        Stores host attributes for network validation tests purpose
        ...
    """

    def __init__(
        self,
        filter_params,
        context="validation",
        nb_url='http://netbox-dev.pop-rj.rnp.br', 
        nb_token='1ba2a61e0dc3e200699b1572451d3be52465d793'
    ) -> None:
        if not CONTEXT and not NB_URL and not NB_TOKEN:
            self.context = context
            self.nb_url = nb_url
            self.nb_token = nb_token
        else:
            self.context = CONTEXT
            self.nb_url = NB_URL
            self.nb_token = NB_TOKEN
        # use pynetbox
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Token {self.nb_token}"})
        self.filter_parameters = filter_params

        InventoryPluginRegister.register("NetBoxInventory", NetBoxInventory)
        try:
            TransformFunctionRegister.register(
                "validation_context_transfer_function", self.inject_host_data_validation)
            TransformFunctionRegister.register(
                "master_context_transfer_function", self.inject_host_data_master)
        except PluginAlreadyRegistered as err:
            print('Plugin already registered:', err)
        self.nb_private_key = NB_PRIVATE_KEY
        self.initNBApi()
        self.initInventory()

    def inject_host_data_validation(self, host):
        # This function receives a Host object for manipulation
        host.hostname = host["custom_fields"]["knetlab_hostname"]
        host.port = host["custom_fields"]["knetlab_port"]
        host.username = host["custom_fields"]["knetlab_username"]
        host.password = host["custom_fields"]["knetlab_pass"]

    def inject_host_data_master(self, host):
        host.port = ""
        host.username = ""
        host.password = ""
        host.platform = "junos"
        # This function receives a Host object for manipulation
        port = self._nb.secrets.secrets.get(
            device_id=host["id"], name="port")
        username = self._nb.secrets.secrets.get(
            device_id=host["id"], name="username")
        password = self._nb.secrets.secrets.get(
            device_id=host["id"], name="password")

        if port and username and password:
            host.port = port.plaintext
            host.username = username.plaintext
            host.password = password.plaintext
        else:
            print("No secrets found on device " + host["name"])
            exit(1)
            # raise Exception("No secrets found on device " + host["name"])
        print("connection_options:",
              dict(host.connection_options))
        host.connection_options["netmiko"] = {"extras": {"timeout": 60}}
        print("Device:", host.name)
        print("Hostname:", host.hostname)
        # print("connection_options:",
        #      dict(host.connection_options))
        # print("Paramiko timeout:",
        #      host.connection_options["paramiko"]["extras"]["timeout"])
        print("----------------")

    def initNBApi(self):
        self._nb = pynetbox.api(
            self.nb_url,
            token=self.nb_token,
            private_key=self.nb_private_key
        )

    def initInventory(self):
        # INVENTORY
        self._nr = InitNornir(
            inventory={
                "plugin": "NetBoxInventory",
                "options": {
                    "nb_url": self.nb_url,
                    "nb_token": self.nb_token,
                    "filter_parameters": self.filter_parameters
                },
                "transform_function": "validation_context_transfer_function" if self.context == "validation" else "master_context_transfer_function"

            }
        )

    def get_inventory(self):
        return self._nr.inventory

    def get_nornir(self):
        return self._nr

    def get_netbox_api(self):
        return self._nb
