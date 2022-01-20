import webbrowser

import click

from spell.api.models import Environment
from spell.cli.exceptions import api_client_exception_handler
from spell.cli.commands.run import create_run_request
from spell.cli.log import logger
from spell.cli.utils import with_emoji, ellipses, command
from spell.cli.utils.command_options import (
    dependency_params,
    workspace_spec_params,
    machine_config_params,
    cli_params,
    description_param,
)
from spell.shared.dependencies import format_apt_versions


@command(
    name="jupyter",
    short_help="Create a jupyter workspace",
    docs="https://spell.ml/docs/workspaces_overview/",
)
@click.argument("name", required=True)
@click.option("--lab", is_flag=True, help="Use Jupyter Lab (default: Jupyter Notebook)")
@click.option(
    "--idle-kernel-timeout",
    type=int,
    default=1800,
    help="Timeout in seconds after which to stop idle kernels",
)
@click.option(
    "--no-activity-timeout",
    type=int,
    default=1800,
    help="Timeout in seconds after which to stop the Jupyter workspace if "
    "there are no running kernels and no user activity",
)
@machine_config_params(exclude_kubernetes=True)
@dependency_params(resource_type="workspace")
@workspace_spec_params
@description_param(resource_type="workspace")
@cli_params
@click.pass_context
def jupyter(
    ctx,
    name,
    lab,
    idle_kernel_timeout,
    no_activity_timeout,
    machine_type,
    python_env_deps,
    pip_packages,
    requirements_file,
    apt_packages,
    commit_ref,
    description,
    envvars,
    docker_image,
    raw_resources,
    conda_file,
    force,
    verbose,
    github_url,
    github_ref,
    provider,
    **kwargs,
):
    """
    Create a Jupyter workspace on Spell.

    The jupyter command is used to create a Jupyter workspace. If executed from within a git repository,
    the HEAD commit (or optionally a different commit specified with --commit-ref) will be copied into
    the Jupyter workspace.  Alternatively, the --github-url option can be used to specify a GitHub
    repository to copy into the workspace. The other options can be used to further configure the
    Jupyter workspace environment.  Once created, the local web browser will open to the
    Jupyter workspace in the Spell web console.
    """
    logger.info("starting jupyter command")
    utf8 = ctx.obj["utf8"]

    # create a run request
    # Note(Brian): We don't actually need a run request (nor are we creating a run); however,
    # create_run_request does some useful validation of common inputs so we call it here.
    run_req = create_run_request(
        ctx,
        machine_type=machine_type,
        python_env_deps=python_env_deps,
        pip_packages=pip_packages,
        requirements_file=requirements_file,
        apt_packages=apt_packages,
        commit_ref=commit_ref,
        description=description,
        envvars=envvars,
        raw_resources=raw_resources,
        conda_file=conda_file,
        force=force,
        verbose=verbose,
        github_url=github_url,
        github_ref=github_ref,
        command=None,
        args=None,
        docker_image=docker_image,
        idempotent=False,
        provider=provider,
        run_type=None,
        distributed=None,
        **kwargs,
    )

    # TODO(Justin): In process of deprecation. pip_env_strings and pip_strings should be renamed
    # pip_env and pip after 0.47.0
    env = Environment(
        apt=format_apt_versions(run_req.apt_packages),
        conda_file=run_req.conda_file,
        pip_env_strings=run_req.pip_env_packages,
        requirements_file=run_req.requirements_file,
        pip_strings=run_req.pip_packages,
        env_vars=run_req.envvars,
        docker_image=docker_image,
    )

    # create the Jupyter workspace
    client = ctx.obj["client"]
    logger.info("sending jupyter workspace request to api")
    with api_client_exception_handler():
        workspace = client.new_jupyter_workspace(
            name=name,
            description=description,
            machine_type=machine_type,
            lab=lab,
            idle_kernel_timeout=idle_kernel_timeout,
            no_activity_timeout=no_activity_timeout,
            attached_resources=run_req.attached_resources,
            environment=env,
            github_url=run_req.github_url,
            github_ref=run_req.github_ref,
            commit_hash=run_req.commit_hash,
            workspace_id=run_req.workspace_id,
        )
    click.echo(with_emoji("💫", "Opening Jupyter workspace '{}'".format(workspace["name"]), utf8) + ellipses(utf8))
    url = "{}/web_redirect/{}/workspaces/{}".format(
        ctx.obj["client_args"]["base_url"], ctx.obj["owner"], workspace["id"]
    )
    webbrowser.open(url)
