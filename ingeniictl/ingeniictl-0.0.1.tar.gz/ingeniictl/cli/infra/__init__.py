import json
import os
import subprocess

import typer

app = typer.Typer()


@app.command()
def disable_resource_protection(
    stack_name: str = typer.Option("", help="Name of Pulumi stack."),
    cwd: str = typer.Option(
        "", help="Set the working directory. Defaults to current working directory."
    ),
):

    if not cwd:
        cwd = os.getcwd()

    # Remove Management Locks
    stack_state = subprocess.run(
        ["pulumi", "stack", "export", "--stack", stack_name, "--cwd", cwd],
        capture_output=True,
    ).stdout

    stack_resources = json.loads(stack_state)["deployment"]["resources"]

    destroy_command = ["pulumi", "destroy", "--yes", "--stack", stack_name]
    for resource in stack_resources:
        if "azure-native:authorization:ManagementLock" in resource["urn"]:
            destroy_command.append("--target")
            destroy_command.append(resource["urn"])

    subprocess.run(destroy_command)

    # Remove Pulumi Locks
    subprocess.run(
        [
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
    )


if __name__ == "__main__":
    app()
