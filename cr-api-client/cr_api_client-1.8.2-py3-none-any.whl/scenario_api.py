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

import requests
from loguru import logger


# Configuration access to Cyber Range endpoint
SCENARIO_API_URL = "http://127.0.0.1:5002"
CA_CERT_PATH = None  # Expect a path to CA certs (see: https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_CERT_PATH = None  # Expect a path to client cert (see: https://requests.readthedocs.io/en/master/user/advanced/)
CLIENT_KEY_PATH = None  # Expect a path to client private key (see: https://requests.readthedocs.io/en/master/user/advanced/)


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: str) -> Any:
    return requests.get(
        f"{SCENARIO_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _post(route: str, **kwargs: str) -> Any:
    return requests.post(
        f"{SCENARIO_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _put(route: str, **kwargs: str) -> Any:
    return requests.put(
        f"{SCENARIO_API_URL}{route}",
        verify=CA_CERT_PATH,
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        **kwargs,
    )


def _delete(route: str, **kwargs: str) -> Any:
    return requests.delete(
        f"{SCENARIO_API_URL}{route}",
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


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _zip_scenario(scenario_path: str, temp_dir: str) -> str:
    """Private function to zip a scenario_path content"""
    zip_file_name = os.path.join(temp_dir, "scenario")

    shutil.make_archive(zip_file_name, "zip", scenario_path)

    return "{}.zip".format(zip_file_name)


def get_version() -> str:
    """Return scenario API version."""
    result = _get("/scenario/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve Scenario API version")

    return result.json()


# -------------------------------------------------------------------------- #
# Scenrio API
# -------------------------------------------------------------------------- #


def scenario_play(
    id_simulation: int,
    scenario_path: str,
    debug_mode: str = "off",
    speed: str = "normal",
    record_video: bool = False,
    write_logfile: bool = False,
    scenario_file_results: str = None,
) -> None:
    """Play scenario on targeted simulation."""

    scenario_success = False

    try:
        data = {
            "idSimulation": id_simulation,
            "debug_mode": debug_mode,
            "speed": speed,
            "record_video": record_video,
            "write_logfile": write_logfile,
        }

        with TemporaryDirectory() as temp_dir:
            # Zipping scenario files
            zip_file_name = _zip_scenario(scenario_path, temp_dir)
            scenario_files = open(zip_file_name, "rb")
            files = {"scenario_files": scenario_files}
            try:
                result = _post("/scenario/start_scenario", data=data, files=files)
            finally:
                scenario_files.close()

        if result.status_code != 200:
            _handle_error(result, "Cannot start scenario at scenario API")

        # Wait for the operation to be completed in backend
        current_status = ""
        while True:
            # Sleep before next iteration
            time.sleep(2)

            logger.info(
                f"  [+] Currently executing scenario for simulation ID '{id_simulation}'..."
            )

            result = _get("/scenario/status_scenario")

            result.raise_for_status()

            result = result.json()

            if "status" in result:
                current_status = result["status"]

                if current_status == "ERROR":
                    error_message = result["error_msg"]
                    raise Exception(
                        "Error during simulation operation: '{}'".format(error_message)
                    )
                elif current_status == "FINISHED":
                    # Operation has ended
                    break

        # Get Scenario Result
        request = _get("/scenario/result_scenario")
        request.raise_for_status()

        result = request.json()

        scenario_results = result["result"]
        scenario_success = scenario_results["success"]

        if scenario_success:
            logger.info(
                f"[+] Scenario was correctly executed on simulation ID '{id_simulation}'"
            )
        else:
            logger.error(
                f"[-] Scenario was executed with errors on simulation ID '{id_simulation}'"
            )

        logger.info(json.dumps(scenario_results, indent=4))

        if scenario_file_results is not None:
            # create file for json results
            try:
                with open(scenario_file_results, "w") as fd:
                    json.dump(scenario_results, fd, indent=4)

                logger.info(
                    f"[+] Scenario results are available here: {scenario_file_results}"
                )

            except Exception as e:
                logger.error(f"[-] Error while writing scenario results: {e}")

        if not scenario_success:
            raise Exception(
                "Some action could not be played. See scenario result for more information."
            )

    except Exception as e:
        raise Exception("Issue when starting scenario execution: '{}'".format(e))

    return scenario_success


def scenario_status(id_simulation: int) -> None:
    """Get scenario status on targeted simulation."""

    try:
        result = _get(
            "/scenario/status_scenario", headers={"Content-Type": "application/json"}
        )

        if result.status_code != 200:
            _handle_error(result, "Cannot get scenario status from scenario API. ")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting scenario status: '{}'".format(e))


def scenario_result(id_simulation: int) -> str:
    """Get scenario result on targeted simulation."""

    try:
        result = _get(
            "/scenario/result_scenario",
            headers={"Content-Type": "application/json"},
            verify=CA_CERT_PATH,
            cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        )

        if result.status_code != 200:
            _handle_error(result, "Cannot get scenario result from scenario API")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting scenario result: '{}'".format(e))
