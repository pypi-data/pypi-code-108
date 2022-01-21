#!/usr/bin/env python3
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
from tempfile import TemporaryDirectory
from typing import Any
from typing import List
from typing import Tuple

import requests
from loguru import logger

import cr_api_client.core_api as core_api


# Configuration access to Cyber Range endpoint
PROVISIONING_API_URL = "http://127.0.0.1:5003"
CA_CERT_PATH = None  # Expect a path to CA certs (see: https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_CERT_PATH = None  # Expect a path to client cert (see: https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_KEY_PATH = None  # Expect a path to client private key (see: https://requests.readthedocs.io/en/master/user/advanced/)


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: str) -> Any:
    return requests.get(
        f"{PROVISIONING_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _post(route: str, **kwargs: str) -> Any:
    return requests.post(
        f"{PROVISIONING_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _put(route: str, **kwargs: str) -> Any:
    return requests.put(
        f"{PROVISIONING_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _delete(route: str, **kwargs: str) -> Any:
    return requests.delete(
        f"{PROVISIONING_API_URL}{route}",
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


def _validate_yaml_file(input_file: str) -> None:
    if os.path.exists(input_file) is not True:
        raise Exception("The provided path does not exist: '{}'".format(input_file))

    if os.path.isfile(input_file) is not True:
        raise Exception("The provided path is not a file: '{}'".format(input_file))

    if os.access(input_file, os.R_OK) is not True:
        raise Exception("The provided file is not readable: '{}'".format(input_file))


def _read_yaml_file(yaml_configuration_file: str) -> str:
    with open(yaml_configuration_file, "r") as fd:
        yaml_content = fd.read()
        return yaml_content


def _zip_resources(resources_path: str, temp_dir: str) -> str:
    """Private function to zip resources path content"""
    zip_file_name = os.path.join(temp_dir, "resources")

    shutil.make_archive(zip_file_name, "zip", resources_path)

    return "{}.zip".format(zip_file_name)


def _raise_error_msg(result: dict) -> None:
    error_msg = "No error message returned"
    if "result" in result:
        if "error_msg" in result["result"]:
            error_msg = result["result"]["error_msg"]
            raise Exception(error_msg)
    else:
        raise Exception(f"No 'result' key in result: {result}")


# -------------------------------------------------------------------------- #
# Provisioning API
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """Return Provisioning API version."""
    result = _get("/provisioning/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve Provisioning API version")

    return result.json()


def provisioning_execute(
    id_simulation: int = None,
    machines_file: str = None,
    provisioning_file: str = None,
    debug: bool = False,
    wait: bool = True,
    timeout: int = 10800,
) -> Tuple[bool, str]:
    """Process YAML configuration file and generate a new provisioning
    chronology.

    """

    if provisioning_file is None:
        raise Exception("provisioning_file parameter cannot be None")

    if (id_simulation is None and machines_file is None) or (
        id_simulation is not None and machines_file is not None
    ):
        raise Exception(
            "Either id_simulation parameter or machines_file parameter is expected in provisioning_execute API"
        )

    if id_simulation is not None:
        log_suffix = f"on simulation ID '{id_simulation}'"
    else:
        log_suffix = f"on machines '{machines_file}'"

    if id_simulation is not None:
        logger.info(f"[+] Starting provisioning {log_suffix}")

        # Check simulation is running
        simulation_dict = core_api.fetch_simulation(id_simulation)
        simulation_status = simulation_dict["status"]
        if simulation_status != "RUNNING":
            raise Exception(
                "The simulation {id_simulation} should have is status RUNNING "
                "(current status is {current_status}) in order to generate provisioning "
                "chronology. Try the command 'cyber_range simu_run {id_simulation}' "
                "to start the simulation.".format(
                    id_simulation=id_simulation, current_status=simulation_status
                )
            )
        machines_yaml = None
    else:
        # Validate input file
        _validate_yaml_file(machines_file)

        # Open and read YAML input files
        machines_yaml = _read_yaml_file(machines_file)

    # Validate input file
    _validate_yaml_file(provisioning_file)

    # Open and read YAML input files
    provisioning_yaml = _read_yaml_file(provisioning_file)

    data = json.dumps(
        {
            "id_simulation": id_simulation,
            "machines_yaml": machines_yaml,
            "provisioning_yaml": provisioning_yaml,
            "debug": debug,
        }
    )

    result = _post(
        "/provisioning/start_provisioning",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot apply provisioning execute")

    result = result.json()
    task_id = result["task_id"]
    success = result["result"] == "STARTED"

    if not success:
        _raise_error_msg(result)

    logger.info(f"[+] Provisioning task ID: {task_id}")

    success = __handle_wait(wait, task_id, log_suffix, timeout=timeout)

    return (success, task_id)


def provisioning_ansible(
    id_simulation: int = None,
    machines_file: str = None,
    playbook_path: str = None,
    target_roles: List[str] = [],
    target_system_types: List[str] = [],
    target_operating_systems: List[str] = [],
    target_names: List[str] = [],
    extra_vars: str = None,
    debug: bool = False,
    wait: bool = True,
    timeout: int = 3600,
) -> Tuple[bool, str]:
    """Apply ansible playbook(s)s on targets."""

    if playbook_path is None:
        raise Exception("provisioning_file parameter cannot be None")

    if (id_simulation is None and machines_file is None) or (
        id_simulation is not None and machines_file is not None
    ):
        raise Exception(
            "Either id_simulation parameter or machines_file parameter is expected in provisioning_ansible API"
        )

    if id_simulation is not None:
        log_suffix = f"on simulation ID '{id_simulation}'"
    else:
        log_suffix = f"on machines '{machines_file}'"

    logger.info(f"[+] Starting provisioning ansible playbook(s) {log_suffix}")

    if id_simulation:
        # Check simulation is running
        simulation_dict = core_api.fetch_simulation(id_simulation)
        simulation_status = simulation_dict["status"]
        if simulation_status != "RUNNING":
            raise Exception(
                "The simulation {id_simulation} should have is status RUNNING "
                "(current status is {current_status}) in order to generate provisioning "
                "chronology. Try the command 'cyber_range simu_run {id_simulation}' "
                "to start the simulation.".format(
                    id_simulation=id_simulation, current_status=simulation_status
                )
            )
        machines_yaml = None
    else:
        # Validate input file
        _validate_yaml_file(machines_file)

        # Open and read YAML input files
        machines_yaml = _read_yaml_file(machines_file)

    data = {
        "id_simulation": id_simulation,
        "machines_yaml": machines_yaml,
        "extra_vars": extra_vars,
        "target_roles": target_roles,
        "target_system_types": target_system_types,
        "target_operating_systems": target_operating_systems,
        "target_names": target_names,
        "debug": debug,
    }

    with TemporaryDirectory() as temp_dir:
        # Zipping resource files
        zip_file_name = _zip_resources(playbook_path, temp_dir)
        resources_file = open(zip_file_name, "rb")
        files = {"resources_file": resources_file}
        try:
            result = _post(
                "/provisioning/start_ansible",
                data=data,
                files=files,
            )
        finally:
            resources_file.close()

    if result.status_code != 200:
        _handle_error(result, "Cannot apply provisioning ansible")

    result = result.json()
    task_id = result["task_id"]
    success = result["result"] == "STARTED"

    if not success:
        _raise_error_msg(result)

    logger.info(f"[+] Provisioning task ID: {task_id}")

    success = __handle_wait(wait, task_id, log_suffix, timeout=timeout)

    return (success, task_id)


def provisioning_inventory(
    id_simulation: int = None,
    machines_file: str = None,
    output_dir: str = None,
    debug: bool = False,
) -> None:
    """Generate ansible inventory files from targets information."""

    if (id_simulation is None and machines_file is None) or (
        id_simulation is not None and machines_file is not None
    ):
        raise Exception(
            "Either id_simulation parameter or machines_file parameter is expected in provisioning_inventory API"
        )

    if id_simulation:
        # Check simulation is running
        simulation_dict = core_api.fetch_simulation(id_simulation)
        simulation_status = simulation_dict["status"]
        if simulation_status != "RUNNING":
            raise Exception(
                "The simulation {id_simulation} should have is status RUNNING "
                "(current status is {current_status}) in order to generate provisioning "
                "chronology. Try the command 'cyber_range simu_run {id_simulation}' "
                "to start the simulation.".format(
                    id_simulation=id_simulation, current_status=simulation_status
                )
            )
        machines_yaml = None
    else:
        # Validate input file
        _validate_yaml_file(machines_file)

        # Open and read YAML input files
        machines_yaml = _read_yaml_file(machines_file)

    data = {
        "id_simulation": id_simulation,
        "machines_yaml": machines_yaml,
        "debug": debug,
    }

    result = _post(
        "/provisioning/generate_inventory",
        data=data,
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot generate ansible inventory")

    try:
        # Create output dir
        if os.path.exists(output_dir):
            raise Exception(f"Output dir already exists: '{output_dir}'")
        os.mkdir(output_dir)

        # Write zip content in a temp file
        zip_content = result.content
        output_zip_file = os.path.join(output_dir, "inventory.zip")
        with open(output_zip_file, "wb") as fd:
            fd.write(zip_content)
            fd.close()

        # Extract zip content
        shutil.unpack_archive(output_zip_file, output_dir, "zip")

        # Remove temp zip file
        os.unlink(output_zip_file)

        logger.info(f"[+] Inventory written in directory '{output_dir}'")
    except Exception as e:
        raise Exception(f"Cannot retrieve inventory: '{e}'")


def provisioning_status(task_id: str) -> dict:
    """Get provisioning status on targeted simulation."""

    data = {"task_id": task_id}

    try:
        result = _post("/provisioning/status_provisioning", data=data)

        if result.status_code != 200:
            _handle_error(result, "Cannot get provisioning status")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting provisioning status: '{}'".format(e))


def provisioning_result(task_id: str) -> str:
    """Get provisioning result on targeted simulation."""

    data = {"task_id": task_id}

    try:
        result = _post(
            "/provisioning/result_provisioning",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(result, "Cannot get provisioning result")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting provisioning result: '{}'".format(e))


def provisioning_stop(task_id: str) -> dict:
    """Stop provisioning task representing by its id."""

    data = {"task_id": task_id}

    result = _post("/provisioning/stop_provisioning", data=data)

    if result.status_code != 200:
        _handle_error(result, "Cannot stop provisioning task")

    return result.json()


def provisioning_wait_until_complete(
    task_id: str, log_suffix: str = None, timeout: int = 3600
) -> dict:
    """wait until provisioning task representing by its id is completed."""

    start_time = time.time()

    current_status = ""

    finished = False
    while not (finished or (time.time() - start_time) > timeout):
        time.sleep(2)
        current_time = time.time()
        elapsed = int(current_time - start_time)
        if log_suffix is not None:
            logger.info(
                f"   [+] Currently provisioning {log_suffix} for {elapsed} seconds (timeout at {timeout} seconds)"
            )
        else:
            logger.info(f"   [+] Currently provisioning for {elapsed} seconds")

        result = _post("/provisioning/status_provisioning", data={"task_id": task_id})
        result.raise_for_status()
        result = result.json()

        if "status" in result:
            current_status = result["status"]

            if current_status == "ERROR":
                error_message = result["error_msg"]
                finished = True
                raise Exception(
                    f"Error during provisioning operation: '{error_message}'"
                )
            elif current_status == "FINISHED":
                finished = True

    if not finished:
        error_msg = f"[-] Unable to terminate operation before timeout of {timeout} seconds. Stopping operation."
        result = provisioning_stop(task_id)
        stopped = result["status"] == "STOPPED"
        if stopped:
            result["result"] = dict()
            result["result"]["error_msg"] = error_msg
            return result
        else:
            raise Exception("Unable to stop provisioning task")

    result = _post("/provisioning/result_provisioning", data={"task_id": task_id})
    result.raise_for_status()
    result = result.json()

    success = result["status"] == "FINISHED" and result["result"]["success"] is True

    if success:
        logger.info("[+] Provisioning was correctly executed")
    else:
        error_msg = result["result"]["error_msg"]
        logger.error(f"[-] Provisioning was executed with error: {error_msg}")

    return result


def __wait_for_the_operation_to_start(task_id: str) -> bool:

    running = False
    timeout = 10
    start_time = time.time()
    while not (running or (time.time() - start_time) > timeout):
        result = _post("/provisioning/status_provisioning", data={"task_id": task_id})
        result.raise_for_status()
        result = result.json()
        running = result["status"] == "RUNNING"
        time.sleep(1)

    if not running:
        logger.error(
            f"[-] Unable to start operation before timeout of {timeout} seconds"
        )

    return running


def __handle_wait(
    wait: bool, task_id: str, log_suffix: str, timeout: int = 3600
) -> bool:

    success = True

    if wait:
        # Wait for the operation to be completed in backend

        result = provisioning_wait_until_complete(
            task_id=task_id, log_suffix=log_suffix, timeout=timeout
        )

        finished = "status" in result and result["status"] == "FINISHED"
        success = finished

        if success:
            if "result" in result:
                if "success" in result["result"]:
                    success = result["result"]["success"] is True

        if not success:
            _raise_error_msg(result)

    else:
        # wait for the operation to start
        running = __wait_for_the_operation_to_start(task_id)

        if not running:
            success = False

    return success
