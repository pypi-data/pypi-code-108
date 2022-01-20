###############################################################################
# (c) Copyright 2020-2021 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import importlib
import json
import os
import shlex
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from os.path import dirname, join
from urllib.parse import urlencode, urlparse, urlunparse

import click
import requests
from LbAPCommon import cern_sso, parse_yaml, render_yaml, validate_yaml
from LbAPCommon.hacks import project_uses_cmt
from LbAPCommon.options_parsing import validate_options

from .utils import (
    check_production,
    create_output_dir,
    pool_xml_catalog,
    recursively_create_input,
)

ANA_PROD_WEB_URL = urlparse(cern_sso.ANA_PROD_HOST)[:2] + ("/dynamic/test-locally/",)


def prepare_test(production_name, job_name, dependent_input=None):
    """Run a local test job for a specific production job"""
    # Check if production exists
    check_production(production_name)

    # Check if job actually exists in production
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    prod_data, checks_data = parse_yaml(render_yaml(raw_yaml))
    validate_yaml(prod_data, checks_data, ".", production_name)
    try:
        job_data = prod_data[job_name]
    except KeyError:
        raise click.ClickException(
            f"Job {job_name} is not found for production {production_name}!"
        )

    application_name, application_version = job_data["application"].rsplit("/", 1)
    options = [*job_data["options"]]

    require_cmt = project_uses_cmt(application_name, application_version)

    params = {
        "application_name": application_name,
        "application_version": application_version,
    }

    if "bk_query" in job_data["input"]:
        params["bk_query"] = job_data["input"]["bk_query"]
    elif "job_name" in job_data["input"]:
        dependent_job = job_data["input"]["job_name"]
        # check we only need to handle one output
        if len(prod_data[dependent_job]["output"]) != 1:
            raise NotImplementedError(
                "Testing jobs that take input from jobs with multiple outputs is not yet supported"
            )
        # figure out the location of the input we need
        if dependent_input is None:
            prod_data[dependent_job]["job_name"] = dependent_job
            dependent_input = recursively_create_input(
                production_name, prod_data[dependent_job], job_name
            )
        # check the input we need exists at the location we think it should
        if not os.path.exists(dependent_input):
            raise OSError(
                f"Local input file not found for {job_name}, please check you have provided the correct path."
            )

        params["bk_query"] = prod_data[dependent_job]["input"]["bk_query"]
        params["override_output_filetype"] = prod_data[dependent_job]["output"][0]
    else:
        raise NotImplementedError(
            "Input requires either a bookkeeping location or a previous job name"
        )

    # only create output directories if this is the job that's about to be run
    # i.e. there are no dependent jobs that need to be run first
    dynamic_dir, out_dir = create_output_dir(production_name, require_cmt)

    if "turbo" in job_data and job_data["turbo"]:
        params["turbo"] = job_data["turbo"]

    if "root_in_tes" in job_data:
        params["root_in_tes"] = job_data["root_in_tes"]

    try:
        data = cern_sso.get_with_cookies(
            urlunparse(ANA_PROD_WEB_URL + ("", urlencode(params), ""))
        )
    except cern_sso.SSOException as e:
        raise click.ClickException(str(e))

    if job_data["automatically_configure"]:
        config_fn = job_name + "_autoconf.py"
        config_path = join(dynamic_dir, production_name, config_fn)
        os.makedirs(dirname(config_path))
        with open(config_path, "wt") as f:
            f.write(data["dynamic_options"]["local_autoconf.py"])
        options.insert(
            0, join("$ANALYSIS_PRODUCTIONS_DYNAMIC", production_name, config_fn)
        )

    prod_conf_fn = "prodConf_DaVinci_00012345_00006789_1.py"
    output_pkl = "--output=output.pkl"
    gaudi_cmd = ["gaudirun.py", "-T", *options, prod_conf_fn, output_pkl]

    if len(job_data["output"]) != 1:
        raise NotImplementedError()
    output_file_type = job_data["output"].pop()

    # force to use the file chosen by the user
    if "bk_query" in job_data["input"]:
        if dependent_input is not None:
            lfns = [dependent_input]
        else:
            lfns = json.dumps([f"LFN:{lfn}" for lfn in data["lfns"]])

            # only need a catalog if we're using Dirac data
            with open(join(out_dir, "pool_xml_catalog.xml"), "wt") as fp:
                fp.write(pool_xml_catalog(data["lfns"]))

    elif "job_name" in job_data["input"]:
        lfns = [dependent_input]

    with open(join(out_dir, prod_conf_fn), "wt") as fp:
        fp.write(
            "\n".join(
                [
                    "from ProdConf import ProdConf",
                    "ProdConf(",
                    "  NOfEvents=-1,",
                    f"  AppVersion='{application_version}',",
                    "  OptionFormat='WGProd',",
                    "  XMLSummaryFile='summaryDaVinci_00012345_00006789_1.xml',",
                    f"  Application='{application_name}',",
                    "  OutputFilePrefix='00012345_00006789_1',",
                    "  XMLFileCatalog='pool_xml_catalog.xml',",
                    f"  InputFiles={lfns},",
                    f"  OutputFileTypes=['{output_file_type}'],",
                    ")",
                ]
            )
        )

    return out_dir, data["env-command"], gaudi_cmd


def prepare_reproduce(pipeline_id, production_name, job_name, test_id="latest"):
    click.secho(
        f"Reproducing test for test {pipeline_id} {production_name} {job_name}",
        fg="green",
    )
    try:
        data = cern_sso.get_with_cookies(
            f"{cern_sso.ANA_PROD_HOST}/dynamic/{pipeline_id}/{production_name}/"
            f"{job_name}/{test_id}/reproduce_locally.json"
        )
    except cern_sso.SSOException as e:
        raise click.ClickException(str(e))

    tmp_dir = tempfile.mkdtemp()

    click.secho(f"Cloning {data['git_repo']}", fg="green")
    subprocess.check_call(["git", "clone", data["git_repo"], tmp_dir])

    click.secho(f"Running test in {tmp_dir}", fg="green")
    os.chdir(tmp_dir)

    click.secho(f"Checking out {data['revision']}", fg="green")
    subprocess.check_call(["git", "checkout", data["revision"]])

    check_production(production_name)

    app_name, app_version = data["env-command"][-1].rsplit("/", 1)
    require_cmt = project_uses_cmt(app_name, app_version)
    dynamic_dir, out_dir = create_output_dir(production_name, require_cmt)

    # Write the dynamic option files
    for filename, filecontent in data["dynamic_options"].items():
        filename = join(dynamic_dir, filename)
        os.makedirs(dirname(filename), exist_ok=True)
        with open(filename, "wt") as f:
            f.write(filecontent)

    # Download the job input
    for filename, url in data["download_files"].items():
        click.secho(f"Downloading {filename}", fg="green")
        filename = join(out_dir, filename)
        os.makedirs(dirname(filename), exist_ok=True)
        with requests.get(url, stream=True) as resp:
            if not resp.ok:
                click.secho(resp.text, fg="red")
                raise click.ClickException("Network request for job file failed")
            with open(filename, "wb") as fp:
                shutil.copyfileobj(resp.raw, fp)

    # Get the LFN from the xml catalog used in the pipeline to regenerate the xml for local operation
    read_xml = ET.parse(join(out_dir, "pool_xml_catalog.xml"))
    lfns_dict = read_xml.find(".//lfn")
    lfns = lfns_dict.attrib["name"]
    with open(join(out_dir, "pool_xml_catalog.xml"), "wt") as fp:
        fp.write(pool_xml_catalog([lfns]))

    env_cmd = data["env-command"]
    return out_dir, env_cmd, data["command"]


def enter_debugging(out_dir, env_cmd, gaudi_cmd, dependent_job=None):
    # This means the requested job depends on another job and has not been told
    # the location of that jobs output
    if dependent_job is not None:
        raise NotImplementedError(
            "Automatic input creation for job-dependent jobs is not implemented in debug mode \n"
            f"The requested job depends on {dependent_job['job_name']}, please provide the location "
            f"of the output file of a local test of {dependent_job['job_name']} by appending "
            '" -i <file_location>" to the debug command'
        )
    with tempfile.NamedTemporaryFile("wt", delete=False) as fp:
        bash_env_fn = fp.name
        fp.write("echo\n")
        fp.write("echo Welcome to analysis productions debug mode:\n")
        fp.write("echo\n")
        fp.write("echo The production can be tested by running:\n")
        fp.write("echo\n")
        fp.write(f"echo {shlex.quote(shlex.join(gaudi_cmd))}\n")
        fp.write("echo\n")
        fp.write(f"rm {shlex.quote(bash_env_fn)}\n")

    cmd = env_cmd + ["bash", "--rcfile", bash_env_fn]
    click.secho(f"Starting lb-run with: {shlex.join(cmd)}", fg="green")

    os.chdir(out_dir)
    os.execlp(cmd[0], *cmd)


def do_options_parsing(env_cmd, out_dir, pkl_file, root_file, job_name, prod_data):
    json_file = join(out_dir, "output.json")

    with importlib.resources.path(
        "LbAPCommon.options_parsing", "gaudi_pickle_to_json.py"
    ) as script_path:
        subprocess.run(
            env_cmd
            + [
                "python",
                script_path,
                "--pkl",
                pkl_file,
                "--output",
                json_file,
                "--debug",
            ],
            text=True,
        )
    return validate_options(json_file, root_file, job_name, prod_data)
