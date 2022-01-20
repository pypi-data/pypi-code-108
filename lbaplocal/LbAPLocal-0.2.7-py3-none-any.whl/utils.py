###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import glob
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from os.path import dirname, join

import click
from LbAPCommon import write_jsroot_compression_options
from LbAPCommon.hacks import setup_lbrun_environment


def validate_environment():
    click.secho("Validating environment", fg="green")
    check_proxy()
    check_cvmfs()


def inside_ap_datapkg():
    """Check if script is run from main directory"""
    if not os.path.exists("./AnalysisProductions.xenv"):
        raise click.ClickException(
            "Running command in wrong directory! Please run from the AnalysisProductions base folder."
        )


def check_proxy():
    try:
        subprocess.check_call(
            ["lb-dirac", "dirac-proxy-info", "--checkvalid"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        raise click.ClickException(
            "No grid proxy found, please get one with lhcb-proxy-init"
        )


def check_cvmfs():
    for path in ["/cvmfs/lhcb.cern.ch", "/cvmfs/lhcb-condb.cern.ch"]:
        if not os.listdir(path):
            raise click.ClickException(f"Missing CVMFS repository: {path}")


def pool_xml_catalog(lfns):
    click.secho("Generating pool XML catalog", fg="green")

    # First check if we already have access
    with tempfile.TemporaryDirectory() as tmp_dir:
        proc = subprocess.run(
            ["lb-dirac", "dirac-bookkeeping-genXMLCatalog", "--LFNs", ",".join(lfns)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=tmp_dir,
        )
        if proc.returncode != 0:
            click.secho("********** stdout was:", fg="red")
            click.echo(proc.stdout)
            click.secho("********** stderr was:", fg="red")
            click.echo(proc.stderr)
            raise click.ClickException(
                f"Failed to generate pool XML catalog with: {proc.args}"
            )
        with open(join(tmp_dir, "pool_xml_catalog.xml"), "rt") as fp:
            return fp.read()


def available_productions():
    """Function that finds all production folders with an info.yaml"""

    # Glob all the info.yaml and extract production name
    folders_with_info = glob.glob("*/info.yaml", recursive=True)
    production_names = []
    for folder in folders_with_info:
        folder_name = dirname(folder)
        production_names.append(folder_name)

    return production_names


def check_production(production_name):
    if production_name not in available_productions():
        raise click.ClickException(
            f"Can't find production {production_name}. Does it have an info.yaml?"
        )


def create_output_dir(production_name, require_cmt):
    """Create the directory structure for testing locally"""

    from datetime import datetime

    date_string = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    testing_dir = join(os.getcwd(), "local-tests", f"{production_name}-{date_string}")
    click.secho(f"Running tests in {testing_dir}", fg="green")
    os.makedirs(testing_dir)

    dynamic_dir = join(testing_dir, "dynamic")
    os.makedirs(dynamic_dir)
    out_dir = join(testing_dir, "output")
    os.makedirs(out_dir)

    main_dynamic_dir = join(os.getcwd(), "dynamic")
    if os.path.exists(main_dynamic_dir):
        click.secho(
            f"Found existing dynamic dir pointing to "
            f"{os.readlink(main_dynamic_dir)}, unlinking",
            fg="green",
        )
        os.unlink(main_dynamic_dir)
    os.symlink(dynamic_dir, main_dynamic_dir)
    write_jsroot_compression_options(dynamic_dir)

    # Create the fake install directory for lb-run
    click.secho(f"Setting CMAKE_PREFIX_PATH to {testing_dir}", fg="green")
    setup_lbrun_environment(testing_dir, os.getcwd(), require_cmt)

    return dynamic_dir, out_dir


def log_popen_pipe(p, pipe_name):
    result = b""
    while p.poll() is None:
        line = getattr(p, pipe_name).readline()
        result += line
        try:
            line = line.decode().strip()
        except UnicodeDecodeError:
            line = repr(line)
        click.echo(line)
    return result


def logging_subprocess_run(args, *, shell=False, cwd=None):
    with subprocess.Popen(
        args, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
    ) as p:
        with ThreadPoolExecutor(2) as pool:
            stdout = pool.submit(log_popen_pipe, p, "stdout")
            stderr = pool.submit(log_popen_pipe, p, "stderr")
            stdout = stdout.result()
            stderr = stderr.result()
    return subprocess.CompletedProcess(args, p.returncode, stdout, stderr)


def production_name_type(production_name):
    return production_name.strip("/")


def recursively_create_input(production_name, dependent_job, desired_job):
    click.secho(
        f"Running {dependent_job['job_name']} to provide the necessary input to {desired_job}",
        fg="green",
    )

    # Run the job the desired job depends on
    result = logging_subprocess_run(
        f"lb-ap test {production_name} {dependent_job['job_name']}", shell=True
    ).stdout.decode()
    # Get the output directory
    output_dir = result.split("\n")[-2].split(" ")[-1]
    # if this is False clearly some other error has occured so don't bother continuing
    if os.path.exists(output_dir):
        # Set the dependent input to lower case to handle inconsistencies between yaml definition and produced file
        dependent_input = (
            output_dir + f"/00012345_00006789_1.{dependent_job['output'][0]}"
        ).lower()

        # set up a dictionary to map lower case output file names to their actual file name locations
        output_files_dict = {
            join(output_dir, name).lower(): join(output_dir, name)
            for name in os.listdir(output_dir)
        }

        # Check we have the desired output
        if dependent_input not in output_files_dict:
            raise OSError(
                f"{dependent_job['job_name']} did not produce the desired output {dependent_input}"
            )

        return output_files_dict[dependent_input]
    else:
        raise OSError(
            f"The expected output directory {output_dir} does not exist! It is likely that the test failed in some"
            " way so the line in stdout upon test success that should provide the output location was not printed."
        )
