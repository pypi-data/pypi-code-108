import click

from spell.api.models import RunRequest
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_CONFIG,
)
from spell.cli.commands.logs import logs
from spell.cli.commands.keys import maybe_write_private_ssh_key_to_disk
from spell.cli.log import logger
from spell.cli.utils import (
    get_or_create_project,
    git_utils,
    parse_utils,
    with_emoji,
    ellipses,
    command,
    try_add_known_host,
)
from spell.cli.utils.parse_utils import parse_conditions, parse_params, validate_attached_resources
from spell.cli.utils.command_options import (
    dependency_params,
    workspace_spec_params,
    machine_config_params,
    cli_params,
    description_param,
    label_param,
    background_option,
    idempotent_option,
    project_option,
    tensorboard_params,
    stop_condition_option,
    timeout_option,
)
from spell.cli.utils.exceptions import ParseException
from spell.shared.dependencies import (
    InvalidDependencyConfig,
    merge_dependencies,
)


@command(name="run", short_help="Execute a new run", docs="https://spell.ml/docs/run_overview/")
@click.argument("command")
@click.argument("args", nargs=-1)
@idempotent_option
@project_option
@machine_config_params()
@dependency_params()
@workspace_spec_params
@tensorboard_params
@description_param()
@label_param
@cli_params
@background_option
@click.option(
    "--distributed",
    type=int,
    metavar="N",
    help="Execute a distributed run using N machines of the specified machine type.",
)
@click.option(
    "--auto-resume/--disable-auto-resume",
    default=None,
    help="Enable or disable auto-resume. NOTE: This is only supported for spot instance machine types",
)
@timeout_option
@stop_condition_option
@click.option(
    "--param",
    "params",
    multiple=True,
    help="Parameter to associate with the run. "
    "Will be substituted into the command for all occurrences of the given name in the format :NAME: "
    "and will be kept as structured data in the UI which is useful for filtering and sorting. "
    "Argument should be specified as NAME=VALUE",
)
@click.pass_context
def run(
    ctx,
    command,
    args,
    machine_type,
    node_group,
    pip_packages,
    python_env_deps,
    requirements_file,
    apt_packages,
    stop_condition,
    docker_image,
    commit_ref,
    description,
    labels,
    envvars,
    raw_resources,
    background,
    conda_file,
    force,
    verbose,
    idempotent,
    timeout,
    provider,
    tensorboard_dir,
    distributed,
    auto_resume,
    project,
    params,
    kubernetes,
    run_type="user",
    **kwargs,
):
    """
    Execute COMMAND remotely on Spell's infrastructure

    The run command is used to create runs and is likely the command you'll use most
    while using Spell. It is intended to be emulate local development. Any code,
    software, binaries, etc., that you can run locally on your computer can be run
    on Spell - you simply put `spell run` in front of the same commands you would use
    locally and they will run remotely. The various options can be used to customize
    the environment in which COMMAND will run.
    """
    if kubernetes:
        for unsupported_field in [
            "distributed",
            "mount",
            "auto-resume",
            "github-url",
            "conda-file",
        ]:
            field_var_name = unsupported_field.replace("-", "_")
            if locals().get(field_var_name) or kwargs.get(field_var_name):
                raise ExitException(f"--{unsupported_field} is not supported for --kubernetes runs")

    logger.info("starting run command")
    try:
        stop_conditions = parse_conditions(stop_condition)
    except ParseException as e:
        raise ExitException(e)
    try:
        params = parse_params(params)
    except ParseException as e:
        raise ExitException(e)

    maybe_write_private_ssh_key_to_disk(ctx)
    try_add_known_host(ctx)

    run_req = create_run_request(
        ctx,
        command,
        args,
        machine_type,
        python_env_deps,
        pip_packages,
        requirements_file,
        apt_packages,
        docker_image,
        commit_ref,
        description,
        envvars,
        raw_resources,
        conda_file,
        force,
        verbose,
        idempotent,
        provider,
        run_type,
        timeout=timeout,
        labels=labels,
        tensorboard_dir=tensorboard_dir,
        distributed=distributed,
        stop_conditions=stop_conditions,
        auto_resume=auto_resume,
        params=params,
        node_group=node_group,
        **kwargs,
    )
    client = ctx.obj["client"]

    # Get or create project
    if project:
        run_req.project_id = get_or_create_project(client, project).id

    # execute the run
    logger.info("sending run request to api")
    with api_client_exception_handler():
        run = client.run(run_req)

    utf8 = ctx.obj["utf8"]
    if run.already_existed:
        click.echo(with_emoji("♻️", "Idempotent: Found existing run {}".format(run.id), utf8) + ellipses(utf8))
    else:
        click.echo(with_emoji("💫", "Casting spell #{}".format(run.id), utf8) + ellipses(utf8))
    if background:
        click.echo("View logs with `spell logs {}`".format(run.id))
    else:
        click.echo(with_emoji("✨", "Stop viewing logs with ^C", utf8))
        ctx.invoke(logs, run_id=str(run.id), follow=True, verbose=verbose, run_warning=True)


def create_run_request(
    ctx,
    command,
    args,
    machine_type,
    python_env_deps,
    pip_packages,
    requirements_file,
    apt_packages,
    docker_image,
    commit_ref,
    description,
    envvars,
    raw_resources,
    conda_file,
    force,
    verbose,
    idempotent,
    provider,
    run_type,
    github_url,
    github_ref,
    timeout=None,
    labels=None,
    distributed=None,
    tensorboard_dir=None,
    stop_conditions=None,
    auto_resume=None,
    params=None,
    node_group=None,
    **kwargs,
):
    if command is None:
        cmd_with_args = None
    else:
        cmd_with_args = " ".join((command,) + args)

    repo = git_utils.detect_repo(
        ctx,
        github_url=github_url,
        github_ref=github_ref,
        force=force,
        description=description,
        commit_ref=commit_ref,
    )
    if description is None:
        description = repo.description

    try:
        python_deps = merge_dependencies(python_env_deps, conda_file, requirements_file, pip_packages).to_payload()
    except InvalidDependencyConfig as e:
        raise ExitException(e, SPELL_INVALID_CONFIG)

    # extract envvars into a dictionary
    curr_envvars = parse_utils.parse_env_vars(envvars)

    # extract attached resources
    attached_resources = validate_attached_resources(raw_resources)

    # TensorBoard checks
    if tensorboard_dir in attached_resources.values():
        raise ExitException("cannot mount into TensorBoard directory")

    return RunRequest(
        machine_type=machine_type,
        node_group=node_group,
        command=cmd_with_args,
        workspace_id=repo.workspace_id,
        workspace_remote_url=repo.workspace_remote_url,
        commit_hash=repo.commit_hash if not repo.has_github() else None,
        uncommitted_hash=repo.uncommitted_hash,
        cwd=repo.relative_path,
        root_directory=repo.root_directory,
        conda_file=python_deps["conda_file"],
        pip_env_packages=python_deps["pip_env"],
        requirements_file=python_deps["requirements_file"],
        pip_packages=python_deps["pip"],
        apt_packages=apt_packages,
        docker_image=docker_image,
        tensorboard_directory=tensorboard_dir,
        description=description,
        timeout=timeout,
        labels=labels,
        envvars=curr_envvars,
        attached_resources=attached_resources,
        run_type=run_type,
        idempotent=idempotent,
        provider=provider,
        local_root=repo.local_root,
        github_url=repo.github_url,
        github_ref=repo.commit_hash if repo.has_github() else None,
        distributed=distributed,
        stop_conditions=stop_conditions,
        auto_resume=auto_resume,
        params=params,
    )
