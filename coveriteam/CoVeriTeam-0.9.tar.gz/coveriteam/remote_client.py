# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from coveriteam.interpreter.file_collector import collect_files
from coveriteam.language.actorconfig import ActorDefinitionLoader
from functools import reduce
import os
import sys
import requests
from pathlib import Path
import zipfile
from xml.etree import ElementTree

CVT_REMOTE_URL = "https://coveriteam.sosy-lab.org/execute"
# CVT_REMOTE_URL = "http://127.0.0.1:5000/execute"  # noqa E800
load_config = ActorDefinitionLoader.load_config
collect_included_files = ActorDefinitionLoader.collect_included_files


def get_included_configs(fs):
    ActorDefinitionLoader.add_constructor("!include", ActorDefinitionLoader.include)
    included_files = []
    for f in fs:
        if Path(f).suffix == ".yml":
            included_files += collect_included_files(load_config(f))
    return included_files


def expand_file_paths(paths):
    expanded = []
    for p in paths:
        if os.path.isabs(p):
            sys.exit(
                "There is a file with absolute path. Please use only relative paths."
            )
        if os.path.isdir(p):
            expanded += [str(x) for x in Path(p).rglob("*") if x.is_file()]
        # For the cases when the arguments are not file paths.
        # TODO: this might even cause problems when a parameter is actually supposed to be a file path, but is not.
        elif not os.path.exists(p):
            pass
        else:
            expanded += [p]
    return expanded


def exec_remotely(config):
    inputs = config.inputs
    cvt_file = config.input_file
    global VERBOSE
    VERBOSE = config.verbose
    # Collect files
    fs = collect_files(cvt_file)
    # TODO check if inputs are actually file paths
    input_paths = [v for _, v in inputs]
    files_needed = [cvt_file] + fs + input_paths
    files_needed = expand_file_paths(files_needed)
    if reduce(lambda x, y: x or y, map(os.path.isabs, files_needed)):
        sys.exit("There is a file with absolute path. Please use only relative paths.")

    # collect all the required yml files.
    files_needed += get_included_configs(files_needed)

    # Preparing inputs
    cp = os.path.commonpath(list(map(os.path.abspath, files_needed)))
    working_dir = os.path.relpath(os.getcwd(), cp)

    json = {
        "coveriteam_inputs": inputs,
        "cvt_program": cvt_file,
        "working_directory": working_dir,
        "filenames": files_needed,
    }
    if config.data_model:
        json["additional_parameters"] = {"data_model": config.data_model}
    res = call_service(json)

    # This is deliberate. 'if res' checks if 200 < status code < 400
    if res is not None:
        show_result(res)


def call_service(data):
    try:
        response = requests.post(CVT_REMOTE_URL, json=data)
        return response
    except requests.exceptions.ConnectionError:
        print("The service disconnected unexpectedly!")
    return None


def show_result(response):
    if response.status_code == 504:
        print(
            "Received response code 504. "
            "Possibly your request couldn't be timely scheduled on the cloud."
        )
        return
    if response.status_code in (400, 500):
        print(response)
        show_error(response)
        return
    output_dir = Path("cvt-output")
    if not output_dir.exists():
        output_dir.mkdir()

    archive_path = output_dir / "cvt_remote_output.zip"

    with archive_path.open("wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(archive_path, "r") as zf:
        zf.extractall(output_dir)
        speculative_output_path = (
            zf.filelist[1].filename.split("/")[0] if len(zf.filelist) > 1 else None
        )

    with (output_dir / "LOG").open("r") as log:
        print(
            "-------------------------------------------------------------------------\n"
            "The following log was produced by the execution of the CoVeriTeam program"
            "on the verifier cloud:"
        )
        print(log.read())
        print(
            "-------------------------------------------------------------------------\n"
            "END OF THE LOG FROM REMOTE EXECUTION"
        )
    if speculative_output_path:
        print(
            "\n\n The output produced by the CoVeriTeam program during execution can be found in the directory: cvt-output/%s"
            % speculative_output_path,
        )

    if VERBOSE:
        if speculative_output_path:
            exec_dir = output_dir.resolve() / Path(speculative_output_path)
            print_output_logs(exec_dir)
        else:
            print("Cannot figure out the names of tool output files.")


def print_output_logs(exec_dir):
    try:
        exec_trace = exec_dir / "execution_trace.xml"
        tool_output_paths = []
        if exec_trace.is_file():
            xml_root = ElementTree.parse(str(exec_trace))  # noqa S314
            for tool_output in xml_root.iter(tag="tool_output"):
                tool_output_paths += [exec_dir / Path(tool_output.text)]
        else:
            print("Couldn't find execution trace. Ouput logs maybe out of order.")
            tool_output_paths = exec_dir.glob("**/output.txt")

        for tool_output_path in tool_output_paths:
            actor_name = tool_output_path.parent.parent.name
            print(
                "\n\n---------------------------------------------------------------\n"
            )
            print("Output produced by the actor: %s \n\n" % actor_name)
            with tool_output_path.open("r") as log:
                print(log.read())
    except Exception:
        print("Something went wrong while printing output logs of tools!")


def show_error(response):
    if response.json().get("message", None):
        print("Server returned an error with  message: %s" % response.json()["message"])
    else:
        print(
            "Unexpected response from the server. Please contact the development team."
        )
