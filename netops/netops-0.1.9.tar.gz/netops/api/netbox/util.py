import requests
import json

from time import sleep
from typing import Any, Dict, List

from .netbox_manager import NetboxManager
from ...utils.paths import PIPELINE_DESCRIPTION


def get_sot_filter_parameters():
    """
	TODO: write docstrings
	"""

    with open(PIPELINE_DESCRIPTION) as f:
        data = json.load(f)

    return data['filter_params']

filter_params = get_sot_filter_parameters()

netbox_manager = NetboxManager(filter_params=filter_params)

nb_url = netbox_manager.nb_url
filter_parameters = netbox_manager.filter_parameters
session = netbox_manager.session
nb_api = netbox_manager.get_netbox_api()


def get_inventory():
    """
	TODO: write docstrings
	"""

    return netbox_manager.get_inventory()


def get_circuits(url: str = f"{nb_url}/api/circuits/circuits/?limits=0", params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
	TODO: write docstrings
	"""
    circuits: List[Dict[str, Any]] = []

    #devices: List[Dict[str, Any]] = []
    #devices_dict = {}

    """
    for param, filter in params.items():
        while url:
            r = session.get(url, params={param: filter})
            if not r.status_code == 200:
                raise ValueError(
                    f"Failed to get data from NetBox instance {nb_url}"
                )

            resp = r.json()
            circuits.extend(resp.get("results"))

            url = resp.get("next")
    """
    
    while url:
        if params:
            r = session.get(url, params=params)
        else:
            r = session.get(url)
        
        if not r.status_code == 200:
            raise ValueError(
                f"Failed to get data from NetBox instance {nb_url}"
            )

        resp = r.json()
        circuits.extend(resp.get("results"))

        url = resp.get("next")

    return circuits


def get_circuit_terminations(params: Dict[str, Any] = None):
    """
	TODO: write docstrings
	"""
    if params:
        circuits = get_circuits(params=params)
    else:
        circuits = get_circuits()
    terminations = {}
    for circuit in circuits:
        termination_a = get_resources(
            url=f"{nb_url}/api/circuits/circuit-terminations/", params={"id": circuit["termination_a"]["id"]})
        termination_z = get_resources(
            url=f"{nb_url}/api/circuits/circuit-terminations/", params={"id": circuit["termination_z"]["id"]})
        c_name = circuit["display"]
        terminations[c_name] = [termination_a[0], termination_z[0]]
    return terminations


def get_resources(url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
	TODO: write docstrings
	"""

    resources: List[Dict[str, Any]] = []

    while url:
        r = session.get(url, params=params)

        if not r.status_code == 200:
            raise ValueError(
                f"Failed to get data from NetBox instance {nb_url}"
            )

        resp = r.json()
        resources.extend(resp.get("results"))

        url = resp.get("next")
    return resources


def get_prefix_ipv4_client(role_name, tenant_name, family_number=4):
    """
	TODO: write docstrings
	"""

    roles = nb_api.ipam.prefixes.filter(
        role=role_name, tenant=tenant_name, family=family_number)
    prefixes = []
    for role in roles:
        prefix = role["prefix"]
        prefixes.append(prefix)
    return prefixes


def get_interface_by_name_device(interface_name, device_name):
    """
	TODO: write docstrings
	"""

    interfaces = nb_api.dcim.interfaces.filter(
        name=interface_name, device=device_name)
    interface = {}
    for i in interfaces:
        interface = i
    return interface


def get_interface_by_label_device(if_label, device_name):
    """
	TODO: write docstrings
	"""

    interfaces = nb_api.dcim.interfaces.filter(
        label=if_label, 
        device=device_name
    )
    for i in interfaces:
        interface = i
    return str(interface)


def get_interface_child_by_parent_device(interface_name, device_name):
    """
	TODO: write docstrings
	"""

    interfaces = nb_api.dcim.interfaces.filter( device=device_name )
    for i in interfaces:
        if str(interface_name) in str(i) and '.' in str(i):
            interface = i
    return str(interface)


def get_interface_parent_by_child_device(interface_name, device_name):
    """
	TODO: write docstrings
	"""

    interfaces = nb_api.dcim.interfaces.filter( device=device_name )
    for i in interfaces:
        phy_int = str(interface_name).split('.')[0]
        if phy_int in str(i) and '.' not in str(i):
            interface = i
    return str(interface)

    
def get_interfaces_unused_device(device_name):
    """
	TODO: write docstrings
	"""

    interfaces = nb_api.dcim.interfaces.filter( device=device_name )
    unused_ints = []
    for i in interfaces:
        if '.' not in i['name'] and i['label'] == '':
            unused_ints.append(str(i))
    return unused_ints


def get_interface_ips_by_interface_name(interface_name, device_name):
    """
	TODO: write docstrings
	"""

    ips = {}
    for ip_address in nb_api.ipam.ip_addresses.all():
        for key in dict(ip_address).keys():
            if key == "assigned_object" and ip_address["assigned_object"]:
                if ip_address["assigned_object"]["name"] == interface_name and ip_address["assigned_object"]["device"]["name"] == device_name:
                    ips[ip_address["family"]["label"]] = ip_address["address"]
    return ips


def get_config_context_data(device_name):
    """
	TODO: write docstrings
	"""

    return nb_api.dcim.devices.filter( name=device_name )["config_context"]


def get_custom_script_result(result_url, nb_token=netbox_manager.nb_token):
    """
	TODO: write docstrings
	"""

    headers = {'Authorization': f"Token {nb_token}" }                    
    r = requests.get(result_url, headers=headers)                       
    status = r.json()['status']['value']

    return r.json(), status
    

def post_custom_script(data, script_urn=None, nb_url=nb_url, nb_token=netbox_manager.nb_token):
    """
	TODO: write docstrings
	"""
    
    headers = {
        'Content-type': 'application/json', 
        'Authorization': f'Token {nb_token}', 
        'Accept': 'application/json; indent=4'
    }
    if type(data) == dict:
        data = json.dumps(data)
    
    response = requests.post(
        nb_url+script_urn,
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        print(f"SUCCESSFULLY made the POST to Netbox Custom Script: {script_urn.split('/')[-2]}")
        print(f"Response MESSAGE: ")
        print(json.dumps(response.json(), indent=4))
        result_url = response.json()['result']['url']
        print(f"Result URL: {result_url}")
        status='pending'
        while status == 'pending':
            rqr, status = get_custom_script_result(result_url, nb_token) # rqr = Result Query Response
            print("Waiting for next query result...")
            sleep(10)

        if status == 'completed':
            print('Script run was SUCCESSFULL!')
            print('Successfull response: ')
            print(json.dumps(rqr, indent=4))
            exit(0)
        else:
            print('Script run FAILED')
            print(f'FAILED status: {status}')
            print('FAILED response: ')
            print(json.dumps(rqr, indent=4))
            exit(1)

    else:
        print(f"POST to Netbox Custom Script {script_urn.split('/')[-1]} FAILED")
        print(f"Response STATUS CODE: {response.status_code}")
        print(f"Response MESSAGE: {response.text}")
        exit(1)
    return

filter_params = get_sot_filter_parameters()