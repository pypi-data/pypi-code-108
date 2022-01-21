#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import json
import os
import shutil
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import requests
from humanize import naturalsize
from loguru import logger
from ruamel.yaml import YAML

# Configuration access to Cyber Range endpoint
CORE_API_URL = "http://127.0.0.1:5000"
# Expect a path to CA certs (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CA_CERT_PATH = None
# Expect a path to client cert (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_CERT_PATH = None
# Expect a path to client private key (see:
# https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_KEY_PATH = None


# Simulation status mapping
map_status = {
    "CREATED": 1,
    "PREPARING": 2,
    "READY": 3,
    "STARTING": 4,
    "PROVISIONING": 5,
    "RUNNING": 6,
    "SCENARIO_PLAYING": 7,
    "STOPPING": 8,
    "DESTROYED": 9,
    "CLONING": 10,
    "PAUSING": 11,
    "UNPAUSING": 12,
    "PAUSED": 13,
    "ERROR": 14,
}


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: Any) -> requests.Response:
    return requests.get(
        f"{CORE_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _post(route: str, **kwargs: Any) -> requests.Response:
    return requests.post(
        f"{CORE_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _put(route: str, **kwargs: Any) -> requests.Response:
    return requests.put(
        f"{CORE_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _delete(route: str, **kwargs: Any) -> requests.Response:
    return requests.delete(
        f"{CORE_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _handle_error(result: requests.Response, context_error_msg: str) -> None:
    if result.headers.get("content-type") == "application/json":
        error_msg = result.json()["message"]
    else:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'.\n"
        f"Error message: '{error_msg}'."
    )


def _simulation_execute_operation(
    operation: str,
    id_simulation: int,
    operation_status: str,
    optional_param: Optional[Any] = None,
) -> str:
    """Generic method to launch API operation on a target simulation."""

    logger.info(
        "[+] Going to execute operation '{}' on simulation ID '{}'".format(
            operation, id_simulation
        )
    )

    # Build URI
    uri = f"/simulation/{id_simulation}/{operation}"
    if optional_param is not None:
        uri = f"{uri}/{str(optional_param)}"

    # Request URI
    result = _get(uri)
    if result.status_code != 200:
        _handle_error(result, "Cannot execute operation '{operation}'")

    # Handle cloning case where a new id_simulation is returned
    if operation == "clone":
        id_simulation = result.json()["id"]

    # Wait for the operation to be completed in backend
    current_status = ""
    while True:
        # Sleep before next iteration
        time.sleep(2)

        logger.info(
            "  [+] Currently executing operation '{}' on "
            "simulation ID '{}'...".format(operation, id_simulation)
        )

        simulation_dict = fetch_simulation(id_simulation)

        current_status = simulation_dict["status"]

        if current_status == "ERROR":
            error_message = simulation_dict["error_msg"]
            raise Exception(
                "Error during simulation operation: '{}'".format(error_message)
            )
        elif current_status != operation_status:
            # Operation has ended
            break

    logger.info(
        "[+] Operation '{}' on simulation ID '{}' was correctly executed".format(
            operation, id_simulation
        )
    )
    logger.info("[+] Current simulation status: '{}'".format(current_status))

    return id_simulation


def _reset_database() -> Any:
    """Reset the database (clean tables) and
    re-populate it with static info (baseboxes, roles...)
    """
    result = _delete("/database/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from core API")

    return result.json()


def _reset_virtclient() -> Any:
    """Ask to stop virtclient VMs."""
    result = _get("/simulation/virtclient_reset")

    if result.status_code != 200:
        _handle_error(result, "Cannot reset virtclient")

    return result.json()


def _validate_yaml_topology_file(yaml_configuration_file: str) -> None:
    if os.path.exists(yaml_configuration_file) is not True:
        raise Exception(
            "The provided YAML configuration path does not exist: '{}'".format(
                yaml_configuration_file
            )
        )

    if os.path.isfile(yaml_configuration_file) is not True:
        raise Exception(
            "The provided YAML configuration path is not a file: '{}'".format(
                yaml_configuration_file
            )
        )

    if os.access(yaml_configuration_file, os.R_OK) is not True:
        raise Exception(
            "The provided YAML configuration file is not readable: '{}'".format(
                yaml_configuration_file
            )
        )


def _read_yaml_topology_file(yaml_configuration_file: str) -> str:
    with open(yaml_configuration_file, "r") as fd:
        yaml_content = fd.read()
        return yaml_content


def _zip_resources(resources_path: Path, temp_dir: Path) -> Path:
    """
    Zip a folder in an archive
    """
    dir_name: str = os.path.basename(os.path.normpath(resources_path))
    zip_base_name: str = os.path.join(temp_dir, dir_name)
    zip_format: str = "zip"
    shutil.make_archive(
        base_name=zip_base_name, format=zip_format, root_dir=resources_path
    )
    return "{}.zip".format(zip_base_name)


def _simu_create_validate_resources_path(resources_path: str) -> None:
    if os.path.exists(resources_path) is not True:
        raise Exception(
            "The provided resources path does not exist: '{}'".format(resources_path)
        )


# -------------------------------------------------------------------------- #
# API helpers
# -------------------------------------------------------------------------- #


###
# Simulation helpers
###


def create_simulation_from_topology(
    topology_file: str = None,
    topology_resources_paths: Optional[List[Path]] = None,
) -> int:

    if topology_resources_paths is None:
        topology_resources_paths = []

    # Create a new simulation model in database based on the provided topology file path."""
    if topology_file is None:
        raise Exception("An topology file is required")

    # Validate YAML configuration file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML configuration file
    yaml_content = _read_yaml_topology_file(topology_file)

    # Parse YAML configuration
    # We use ruamel.yaml because it keeps anchors and
    # aliases in memory. It is very convenient when the simulation
    # is stored/fetched (references are kept!)
    loader = YAML(typ="rt")
    topology_content = loader.load(yaml_content)

    if "name" not in topology_content:
        raise Exception(
            "There should be a 'name' element in the YAML configuration file"
        )
    name = topology_content["name"]

    if "nodes" not in topology_content:
        raise Exception(
            "There should be a 'nodes' structure in the YAML configuration file"
        )

    if "links" not in topology_content:
        raise Exception(
            "There should be a 'links' structure in the YAML configuration file"
        )

    simulation_dict = {"name": name, "network": topology_content, "resources_paths": []}

    # Verify that we do not have the same resources path in the list
    if len(set(topology_resources_paths)) != len(topology_resources_paths):
        raise Exception("Identical resources paths have been given")

    for resource in topology_resources_paths:
        # Validate resources path
        _simu_create_validate_resources_path(resource)
        # take the absolute path
        simulation_dict["resources_paths"].append(os.path.abspath(resource))

    id_simulation = add_simulation(simulation_dict)

    # Prepare disk resources
    _simulation_execute_operation("prepare", id_simulation, "PREPARING")

    return id_simulation


def create_simulation_from_basebox(
    basebox_id: str, add_internet: bool = False, add_host: bool = False
) -> int:
    """Create a new simulation model in database based on the provided basebox id, with optionnaly internet and/or host connectivity."""

    if basebox_id is None:
        raise Exception("A basebox ID is required")

    # Create an topology with the provided basebox ID
    try:
        basebox = fetch_basebox(basebox_id)
    except Exception:
        raise Exception(
            f"Cannot find basebox in database from basebox ID '{basebox_id}'"
        )

    role = basebox["role"]
    nb_proc = basebox["nb_proc"]
    memory_size = basebox["memory_size"]

    yaml_content = f"""---
name: "{basebox_id}"
nodes:

  - &switch
    type: switch
    name: "switch"

  - &client
    type: virtual_machine
    name: "client"
    basebox_id: "{basebox_id}"
    nb_proc: {nb_proc}
    memory_size: {memory_size}
    roles: ["{role}"]
"""

    if add_host:
        yaml_content += """
  - &host_machine
    type: host_machine
    name: "host_machine"
"""

    if add_internet:
        # add default route to gateway, a gateway and a switch to plug the gateway and the router
        yaml_content += """
  - &router
    type: router
    name: "router"
    routes:
      - "0.0.0.0/0 -> 192.168.23.2"

  - &switch_internet
    type: switch
    name: "switch_internet"

  - &physical_gateway
    type: physical_gateway
    name: "physical_gateway"
"""
    else:
        yaml_content += """
  - &router
    type: router
    name: "router"
"""

    yaml_content += """
links:

  - switch: *switch
    node: *router
    params:
      ip: "192.168.2.1/24"
      dhcp_nameserver: "8.8.8.8"

  - switch: *switch
    node: *client
    params:
      ip: "192.168.2.2/24"
"""

    if add_host:
        yaml_content += """
  - switch: *switch
    node: *host_machine
    params:
      ip: "192.168.2.3/24"
"""

    if add_internet:
        yaml_content += """
  - switch: *switch_internet
    node: *router
    params:
      ip: "192.168.23.1/24"

  - switch: *switch_internet
    node: *physical_gateway
    params:
      ip: "192.168.23.2/24"
"""

    loader = YAML(typ="rt")
    network_structure = loader.load(yaml_content)

    simulation_dict = {"name": str(basebox_id), "network": network_structure}

    id_simulation = add_simulation(simulation_dict)

    # Prepare disk resources
    _simulation_execute_operation("prepare", id_simulation, "PREPARING")

    return id_simulation


###
# Topology helpers
###


def topology_file_add_websites(
    topology_file: str, websites: List[str], switch_name: str
) -> str:
    """Add docker websites node to a given topology, and return the updated topology."""

    # Validate YAML topology file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML topology file
    topology_yaml = _read_yaml_topology_file(topology_file)

    # Update topology with the API
    topology_yaml = topology_add_websites(topology_yaml, websites, switch_name)

    return topology_yaml


def topology_file_add_dga(
    topology_file: str,
    algorithm: str,
    switch_name: str,
    number: int,
    resources_dir: str,
) -> (str, List[str]):
    """Add docker empty websites node with DGA to a given topology, and return the updated topology."""

    # Validate

    # Validate YAML topology file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML topology file
    topology_yaml = _read_yaml_topology_file(topology_file)

    # Update topology with the API
    (topology_yaml, domains) = topology_add_dga(
        topology_yaml, algorithm, switch_name, number, resources_dir
    )

    return topology_yaml, domains


# -------------------------------------------------------------------------- #
# Core API
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """Return Core API version."""
    result = _get("/simulation/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve Core API version")

    return result.json()


def reset() -> Any:
    """Reset the database (clean tables) and
    re-populate it with static info (baseboxes, roles...)
    """

    _reset_database()
    _reset_virtclient()


def add_simulation(simulation_dict: dict) -> int:
    """Create simulation and return a simulation ID."""

    # Get the paths if some have been provided
    resources_paths = simulation_dict.pop("resources_paths", [])

    data = json.dumps(simulation_dict)

    # Creation of a folder containing all the resources, this folder will then be zipped
    with TemporaryDirectory() as main_resources:

        # copy all resources in the main temporary folder
        for resource in resources_paths:
            if os.path.isdir(resource):
                shutil.copytree(
                    resource,
                    os.path.join(
                        main_resources, os.path.basename(os.path.normpath(resource))
                    ),
                )
            elif os.path.isfile(resource):
                shutil.copyfile(
                    resource,
                    os.path.join(
                        main_resources, os.path.basename(os.path.normpath(resource))
                    ),
                )
            else:
                raise Exception(f"Can not copy {resource}")

        # We have to create a new temporary folder to host the archive
        with TemporaryDirectory() as temp_dir:
            zip_file_name = _zip_resources(main_resources, temp_dir)
            resources_file = open(zip_file_name, "rb")
            files = {"resources_file": resources_file, "data": data}
            try:
                result = _post(
                    "/simulation/",
                    files=files,
                )
            finally:
                resources_file.close()

    if not main_resources:
        result = _post(
            "/simulation/",
            data=data,
            headers={"Content-Type": "application/json"},
        )

    if result.status_code != 200:
        _handle_error(result, "Cannot post simulation information to core API")

    id_simulation = result.json()["id"]
    return id_simulation


def simulation_status(id_simulation: int) -> str:
    """Return only the status of the simulation"""
    result = _get(f"/simulation/{id_simulation}/status")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from core API")

    return result.json()


def fetch_simulation(id_simulation: int) -> dict:
    """Return a simulation dict given a simulation id."""
    result = _get(f"/simulation/{id_simulation}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from core API")

    simulation_dict = result.json()

    return simulation_dict


def fetch_simulations() -> List[Any]:
    """Return all simulations."""
    result = _get("/simulation/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from core API")

    simulation_list = result.json()
    return simulation_list


def delete_simulation(id_simulation: int) -> Any:
    """Delete a simulation from database."""

    # Destroy simulation if it is running
    if simulation_status(id_simulation) == "RUNNING":
        _simulation_execute_operation("destroy", id_simulation, "STOPPING")

    _simulation_execute_operation("delete_snapshots", id_simulation, "STOPPING")

    # Delete simulation nodes
    delete_nodes(id_simulation)

    # Delete simulation
    result = _delete(f"/simulation/{id_simulation}")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete simulation from core API")

    return result.json()


def update_simulation(id_simulation: int, simulation_dict: dict) -> Any:
    """Update simulation information information given a simulation id
    and a dict containing simulation info.
    """
    data = json.dumps(simulation_dict)
    result = _put(
        f"/simulation/{id_simulation}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update simulation information")

    return result.json()


def fetch_simulation_topology(id_simulation: int) -> Any:
    """Return the topology of a simulation."""
    result = _get(f"/simulation/{id_simulation}/topology")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation topology info")

    return result.json()


def fetch_simulation_topology_yaml(id_simulation: int) -> Any:
    """Return the YAML topology content of a simulation."""
    result = _get(f"/simulation/{id_simulation}/topology_yaml")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation topology info")

    return result.json()


def fetch_assets(id_simulation: int) -> Any:
    """Return the list of the assets
    of a given simulation. It corresponds to
    the list of the nodes with some additional
    information.
    """
    result = _get(f"/simulation/{id_simulation}/assets")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve assets from core API")

    return result.json()


def fetch_node(node_id: int) -> Any:
    """Return a node given its ID"""
    result = _get(f"/node/{node_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node from core API")

    return result.json()


def fetch_node_by_name(id_simulation: int, node_name: str) -> Any:
    """Return a node given its name"""

    result = _get(f"/simulation/{id_simulation}/node/{node_name}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation nodes from core API")

    return result.json()


def fetch_nodes_by_roles(id_simulation: int) -> Any:
    """Return a dict wkere keys are roles (such as 'ad', 'file_server', 'client', ...) and
    values are nodes.

    """
    result = _get(f"/simulation/{id_simulation}/nodes_by_roles")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve nodes")

    roles_dict = result.json()
    return roles_dict


def delete_node(id_node: int) -> Any:
    """Delete simulation node given its ID."""
    # Fetch virtual node network interfaces
    network_interfaces = fetch_node_network_interfaces(id_node)

    # Delete each network interfaces
    for network_interface in network_interfaces:
        delete_network_interface(network_interface["id"])

    # Delete node
    result = _delete(f"/node/{id_node}")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete node")

    return result.json()


def fetch_nodes(id_simulation: int) -> Any:
    """Return simulation nodes dict given
    a simulation ID, where keys are node names.
    """
    result = _get(f"/simulation/{id_simulation}/node")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation nodes from core API")

    return result.json()


def fetch_virtual_machines(id_simulation: int) -> List[dict]:
    """Return simulation virtual machines dict given a simulation ID,
    where keys are virtual machine names.
    """
    results = fetch_nodes(id_simulation)

    vm_only = filter(lambda m: m["type"] == "virtual_machine", results)
    return list(vm_only)


def delete_nodes(id_simulation: int) -> str:
    """Delete simulation nodes given a simulation ID."""

    # Fetch simulation nodes
    result = _get(f"/simulation/{id_simulation}/node")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete simulation nodes")

    nodes_list = result.json()

    # Delete each node
    for node in nodes_list:
        delete_node(node["id"])

    result_json = "{}"
    return result_json


def update_node(node_id: int, node_dict: dict) -> Any:
    """Update node information given a node id and a dict containing
    node data.
    """
    data = json.dumps(node_dict)
    result = _put(
        f"/node/{node_id}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update node information with core API")

    return result.json()


def get_node_statistics_by_id(id_node: int) -> Any:
    """
    Return aggregated statistics from CPU, memory, block devices and network interfaces.
    """
    result = _get(f"/node/{id_node}/stats")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node statistics")

    return result.json()


def node_memorydump(id_node: int) -> Any:
    """
    Return RAM dump of a node in a running simulation
    """
    file_path_key = "file_path"
    file_size_key = "file_size"
    status_key = "status"

    result = _get(f"/node/{id_node}/memorydump")

    if (
        result.status_code != 200
        or status_key not in result.json()
        or result.json()[status_key] != "STARTED"
    ):
        _handle_error(result, "Cannot initiate node memory dump fom core API")

    logger.info("[+] Initialized memory dump of node '{}'...".format(id_node))

    # Wait for the operation to be completed in backend
    # Note : loop inspired from _simulation_execute_operation
    while True:
        # Sleep before next iteration
        time.sleep(2)

        # Fetch the current status of the memdump
        result = _get(f"/node/{id_node}/memorydump_status")

        if result.status_code != 200:
            _handle_error(result, "Cannot get status of node memory dump fom core API")

        result_json = result.json()
        if not (
            all(k in result_json for k in (file_path_key, file_size_key, status_key))
        ):
            raise Exception(
                f"Contents of memory dump status update is not in the expected format (attributes '{file_path_key}', '{file_size_key}' and '{status_key}' expected)"
            )

        # Log info on progression
        if result_json[status_key] == "PROGRESS":
            logger.info(
                "  [+] Currently performing memory dump of node '{}' (current dump file size is {})...".format(
                    id_node, naturalsize(result_json[file_size_key], binary=True)
                )
            )
        elif result_json[status_key] == "SUCCESS":
            break
        else:
            raise Exception(
                "Error during memory dump of node {} operation: '{}'".format(
                    id_node, result_json[status_key]
                )
            )

    logger.info(
        "[+] Node memory dump (raw dump with libvirt) obtained, and placed in file {} ({}) on the server.".format(
            result_json[file_path_key],
            naturalsize(result_json[file_size_key], binary=True),
        )
    )

    return result_json[file_path_key], result_json[file_size_key]


def fetch_node_network_interfaces(id_node: int) -> Any:
    """Return network interfaces list given a node ID."""
    result = _get(f"/node/{id_node}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node network interfaces")

    return result.json()


def fetch_simulation_network_interfaces(id_simulation: int) -> Any:
    """Return network interfaces list given a simulation ID."""
    result = _get(f"/simulation/{id_simulation}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation network interfaces")

    return result.json()


def fetch_network_interface_by_mac(id_simulation: int, mac_address: str) -> Any:
    """Return network interface list given a mac address."""
    # Fetch node network interfaces
    result = _get(f"/simulation/{id_simulation}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve network interfaces")

    network_interfaces = result.json()

    for network_interface in network_interfaces:
        if network_interface["mac_address"] == mac_address:
            return network_interface
    else:
        return None


def delete_network_interface(id_network_interface: int) -> Any:
    """Delete network interface given an id."""
    result = _delete(f"/network_interface/{id_network_interface}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node network interfaces from core API")

    return result.json()


def update_network_interface(
    id_network_interface: int, network_interface_dict: dict
) -> Any:
    """Update network interface information information given a network interface id and a
    dict containing network info.

    """
    data = json.dumps(network_interface_dict)
    result = _put(
        f"/network_interface/{id_network_interface}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update network interface information")

    return result.json()


def fetch_baseboxes() -> Any:
    """Return baseboxes list."""
    result = _get("/basebox")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve baseboxes list from core API")

    baseboxes = result.json()
    return baseboxes


def fetch_basebox(id_basebox: str) -> Any:
    """Return basebox given a basebox id."""
    result = _get(f"/basebox/id/{id_basebox}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from core API")

    basebox = result.json()
    return basebox


def reload_baseboxes() -> Any:
    """
    Call the cyber range API to reload the list of available baseboxes
    :return:
    """
    result = _get("/basebox/reload")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from core API")

    return result.json()


def verify_baseboxes() -> Any:
    """
    Call the API to verify the checksums of the baseboxes
    :return:
    """
    result = _get("/basebox/verify")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from core API")

    return result.json()


def verify_basebox(id_basebox: int) -> Any:
    """
    Call the API to verify the checksum of the given basebox
    :param id_basebox: the id of the basebox
    :return:
    """
    result = _get(f"/basebox/verify/{id_basebox}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from core API")

    return result.json()


def fetch_domains() -> Dict[str, str]:
    """Returns the mapping domain->IP"""

    # FIXME(multi-tenant): we should retrieve domains according to a simulation id
    result = _get("/network_interface/domains")

    if result.status_code != 200:
        _handle_error(result, "Error while fetching domains")

    return result.json()


def fetch_websites() -> Any:
    """Return websites list."""
    result = _get("/website")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve websites list from core API")

    websites = result.json()
    return websites


def topology_add_websites(
    topology_yaml: str, websites: List[str], switch_name: str
) -> str:
    """Add docker websites node to a given topology, and return the updated topology."""

    data_dict = {
        "topology_yaml": topology_yaml,
        "websites": websites,
        "switch_name": switch_name,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/topology/add_websites",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding websites to a topology")

    topology_yaml = result.json()["topology_yaml"]

    return topology_yaml


def topology_add_dga(
    topology_yaml: str,
    algorithm: str,
    switch_name: str,
    number: int,
    resources_dir: str,
) -> Tuple[str, List[str]]:
    """Add docker empty websites with DGA node to a given topology, and return the updated topology
    associated with the domains."""

    data_dict = {
        "topology_yaml": topology_yaml,
        "algorithm": algorithm,
        "switch_name": switch_name,
        "number": number,
        "resources_dir": resources_dir,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/topology/add_dga",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding websites to a topology")

    topology_yaml = result.json()["topology_yaml"]
    domains = result.json()["domains"]

    return topology_yaml, domains


def tools_generate_domains(
    algorithm: str,
    number: int,
) -> List[str]:
    """
    Generate domain names according to the given algorithm
    :param algorithm: algorithm to use
    :param number: number of domains to generate
    :return: A list of domains
    """
    data_dict = {
        "algorithm": algorithm,
        "number": number,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/domain/generate_domains",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while generating domains")

    domains = result.json()["domains"]

    return domains


def fetch_topologies() -> Any:
    """Return topologies list."""
    result = _get("/topology")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve topologies list from core API")

    topologies = result.json()
    return topologies


###
# Simulation commands
###


def start_simulation(id_simulation: int, use_install_time: bool = False) -> None:
    # Check that no other simulation is running
    simulation_list = fetch_simulations()
    for simulation in simulation_list:
        if simulation["status"] == "RUNNING":
            raise Exception(
                "Cannot start a new simulation, as the simulation '{}' is "
                "already running".format(simulation["id"])
            )

    # Initiate the simulation
    _simulation_execute_operation(
        "start", id_simulation, "STARTING", optional_param=use_install_time
    )


def pause_simulation(id_simulation: int) -> None:
    _simulation_execute_operation("pause", id_simulation, "PAUSING")


def unpause_simulation(id_simulation: int) -> None:
    _simulation_execute_operation("unpause", id_simulation, "UNPAUSING")


def halt_simulation(id_simulation: int) -> None:
    _simulation_execute_operation("stop", id_simulation, "STOPPING")


def destroy_simulation(id_simulation: int) -> None:
    _simulation_execute_operation("destroy", id_simulation, "STOPPING")


def clone_simulation(id_simulation: int) -> int:
    id_new_simulation = _simulation_execute_operation("clone", id_simulation, "CLONING")
    return id_new_simulation


def tap_simulation(id_simulation: int, iface: str) -> None:
    """Redirect network traffic to the tap interface."""
    result = _get(f"/simulation/{id_simulation}/tap/{iface}")

    if result.status_code != 200:
        _handle_error(
            result, "Cannot activate network traffic redirection from core API"
        )


def untap_simulation(id_simulation: int, iface: str) -> None:
    """Stop redirection of network traffic to the tap interface."""
    result = _get(f"/simulation/{id_simulation}/untap/{iface}")

    if result.status_code != 200:
        _handle_error(result, "Cannot stop network traffic redirection from core API")


def snapshot_simulation(id_simulation: int) -> str:
    """Create a snapshot of a simulation.

    All the files will be stored to
    /cyber-range-catalog/simulations/<hash campaign>/<timestamp>/

    This API call returns the path where the topology file will be stored.

    Parameters
    ----------
    id_simulation: int
        Simulation to snapshot

    """

    # simu_snap can only be done on a RUNNING simulation
    if simulation_status(id_simulation) != "RUNNING":
        raise Exception(
            "Cannot create a snapshot of the simulation, as the simulation '{}' is "
            "not running".format(id_simulation)
        )

    # Call snapshot API
    result = _post(f"/simulation/{id_simulation}/snapshot")
    if result.status_code != 200:
        _handle_error(result, "Error while creating snapshot")

    yaml: str = result.json()

    logger.info(f"[+] Starting the snapshot of simulation {id_simulation}...")
    while simulation_status(id_simulation) != "SNAPSHOT":
        time.sleep(1)

        simulation_dict = fetch_simulation(id_simulation)
        current_status = simulation_dict["status"]
        if current_status == "ERROR":
            error_message = simulation_dict["error_msg"]
            raise Exception(
                "Error during simulation snapshot: '{}'".format(error_message)
            )

    logger.info("[+] Snapshot process has started")

    while simulation_status(id_simulation) != "RUNNING":
        logger.info("  [+] Snapshot in progress...")
        time.sleep(1)

        simulation_dict = fetch_simulation(id_simulation)
        current_status = simulation_dict["status"]
        if current_status == "ERROR":
            error_message = simulation_dict["error_msg"]
            raise Exception(
                "Error during simulation snapshot: '{}'".format(error_message)
            )

    return yaml


def virtclient_status() -> Any:
    """Get virtclient service status."""
    result = _get("/simulation/virtclient_status")

    if result.status_code != 200:
        _handle_error(result, "Cannot get virtclient service status")

    simulation_dict = result.json()
    return simulation_dict


def add_dns_entries(id_simulation: int, dns_entries: Dict[str, str]) -> str:
    """Add volatile DNS entries to the current simulation. Volatile means that it is not
    stored in database.

    """

    data = json.dumps(dns_entries)
    result = _post(
        f"/simulation/{id_simulation}/add_dns_entries",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding DNS entries")


def generate_malicious_domains(algorithm: str = None, number: int = 1) -> List[str]:
    """Generate and return a list of malicious domains."""

    data_dict = {
        "algorithm": algorithm,
        "number": number,
    }
    data = json.dumps(data_dict)

    result = _post(
        "/topology/generate_malicious_domains",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding DNS entries")

    domains = result.json()
    return domains["domains"]
