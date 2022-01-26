import json
import os
import subprocess
import traceback

import typer

from ingeniictl.clients import log_client

from .main import app


# ingeniictl -> infra -> disable_resource_protection


def _get_pulumi_stack_state(stack_name: str, cwd: str):
    return subprocess.run(
        ["pulumi", "stack", "export", "--stack", stack_name, "--cwd", cwd],
        capture_output=True,
    ).stdout


def _remove_management_locks(stack_name: str, cwd: str):

    stack_state = _get_pulumi_stack_state(stack_name, cwd)
    stack_resources = json.loads(stack_state)["deployment"]["resources"]

    remove_command = ["pulumi", "destroy", "--yes", "--stack", stack_name]

    locks = []

    for resource in stack_resources:
        urn = resource["urn"]

        if "azure-native:authorization:ManagementLock" in urn:
            locks.append("--target")
            locks.append(urn)

    # Do not run the 'remove_command' unless we have management locks to remove.
    if len(locks) >= 2:
        log_client.info(f"Removing {int(len(locks)/2)} Azure Management Locks...")
        subprocess.run(remove_command + locks)
    else:
        log_client.info(f"No Azure Management Locks found.")


def _remove_pulumi_protect_flags(stack_name: str, cwd: str):
    remove_command = [
        "pulumi",
        "state",
        "unprotect",
        "--all",
        "--yes",
        "--stack",
        stack_name,
        "--cwd",
        cwd,
    ]

    log_client.info(f"Removing Pulumi protect flags...")
    subprocess.run(remove_command)


@app.command()
def disable_resource_protection(
    pulumi_stack_name: str = typer.Argument(
        ..., help="Name of the Pulumi stack. e.g. 'ingenii/dev' "
    ),
    pulumi_project_dir: str = typer.Option(
        "",
        help="This is the directory that has the 'Pulumi.yaml' file. Defaults to current working directory.",
    ),
) -> None:
    if not pulumi_project_dir:
        pulumi_project_dir = os.getcwd()

    try:
        _remove_management_locks(pulumi_stack_name, pulumi_project_dir)
        _remove_pulumi_protect_flags(pulumi_stack_name, pulumi_project_dir)
        log_client.ok("Resource protection disabled successfully.")
    except Exception as e:
        log_client.err("Unable to disable the resource protection.")
        log_client.err(traceback.format_exc())
