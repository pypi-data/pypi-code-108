import click
import os

from spell.cli.commands.logs import logs
from spell.cli.commands.keys import maybe_write_private_ssh_key_to_disk
from spell.cli.commands.run import create_run_request
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_CONFIG,
    SPELL_BAD_REPO_STATE,
)
from spell.cli.log import logger
from spell.cli.utils import (
    git_utils,
    parse_utils,
    with_emoji,
    ellipses,
    group,
    try_add_known_host,
)
from spell.cli.utils.command_options import (
    dependency_params,
    workspace_spec_params,
    cli_params,
    description_param,
    background_option,
)
from spell.cli.utils.exceptions import ParseException


@group(
    name="workflow",
    short_help="Execute workflows",
    help="Execute workflows on Spell",
    docs="https://spell.ml/docs/workflow_overview/",
)
@click.pass_context
def workflow(ctx):
    pass


@workflow.command(
    name="create",
    short_help="Create a new workflow",
    help="Creates a new workflow",
    docs="https://spell.ml/docs/workflow_overview/#creating-a-workflow-script",
)
@click.pass_context
@click.argument("command")
@click.argument("args", nargs=-1)
@click.option(
    "--local",
    is_flag=True,
    help="Execute command locally instead of remotely on Spell's infrastructure",
)
@click.option(
    "-r",
    "--repo",
    "repo_paths",
    multiple=True,
    metavar="LABEL=PATH[:COMMIT_HASH]",
    help="Add a git repository at a specific commit to this workflow by specifying LABEL=PATH, "
    "where PATH is a path to a local git repository on disk and LABEL is a label to refer to "
    "this snapshot in future run requests. COMMIT_HASH can optionally be specified "
    "by LABEL=PATH[:COMMIT_HASH]. "
    "If no COMMIT_HASH is specified, the currently checked out commit of the repo will be used.",
)
@click.option(
    "--github-repo",
    "github_urls",
    multiple=True,
    metavar="LABEL=URL[:REF]",
    help="Add a GitHub repository at a specific ref to this workflow by specifying LABEL=URL, "
    "where URL is a url to a GitHub repository and LABEL is a label to refer to "
    "this snapshot in future run requests. REF can optionally be specified "
    "by LABEL=PATH[:REF], it can be a branch, commit hash, or label, "
    "and will be resolved to a commit hash immediately. "
    "If no REF is specified, master will be used.",
)
@dependency_params(resource_type="workflow")
@workspace_spec_params
@description_param(resource_type="workflow")
@cli_params
@background_option
def create(
    ctx,
    command,
    args,
    local,
    repo_paths,
    github_urls,
    python_env_deps,
    pip_packages,
    requirements_file,
    apt_packages,
    docker_image,
    commit_ref,
    description,
    envvars,
    background,
    conda_file,
    force,
    verbose,
    github_url,
    github_ref,
    **kwargs,
):
    """
    Execute WORKFLOW either remotely or locally

    The workflow command is used to create workflows which manage other runs.
    Complex machine learning applications often require multi-stage pipelines
    (e.g., data loading, transforming, training, testing, iterating). Workflows
    are designed to help you automate this process. While a workflow executes
    much like a normal run, it is capable of launching other runs that are
    all associated with each other. A workflow must specify every git commit that
    will be used by the given workflow script using the `--repo` flag.
    The various other options can be used to customize the environment that the
    workflow script runs in.
    """
    run_req = None
    try:
        repo_paths = parse_utils.parse_repos(repo_paths)
    except ParseException as e:
        raise ExitException(
            click.wrap_text(
                "Incorrect formatting of repo '{}', it must be " "<label>=<repo_path>[:commit_ref]".format(e.token)
            ),
            SPELL_INVALID_CONFIG,
        )
    workspace_specs = git_utils.sync_repos(ctx, repo_paths, force)
    try:
        github_specs = parse_utils.parse_github_repos(github_urls)
    except ParseException as e:
        raise ExitException(
            click.wrap_text(
                "Incorrect formatting of GitHub repo '{}', it must be " "<label>=<githubrepo_url>[:ref]".format(e.token)
            ),
            SPELL_INVALID_CONFIG,
        )
    dupe_labels = [label for label in workspace_specs if label in github_specs]
    if len(dupe_labels) > 0:
        click.echo(
            click.wrap_text("Each repo label must be unique. The following labels are duplicated:"),
            err=True,
        )
        for label in dupe_labels:
            click.echo(click.wrap_text(" - " + label), err=True)
        raise ExitException("Invalid Git Repo(s)", SPELL_BAD_REPO_STATE)

    if not local:
        maybe_write_private_ssh_key_to_disk(ctx)
        try_add_known_host(ctx)

    if not local:
        run_req = create_run_request(
            ctx=ctx,
            command=command,
            args=args,
            machine_type="CPU",
            python_env_deps=python_env_deps,
            pip_packages=pip_packages,
            requirements_file=requirements_file,
            apt_packages=apt_packages,
            docker_image=docker_image,
            commit_ref=commit_ref,
            description=description,
            envvars=envvars,
            raw_resources=[],
            conda_file=conda_file,
            force=force,
            verbose=verbose,
            idempotent=False,
            provider=None,
            run_type="workflow",
            github_url=github_url,
            github_ref=github_ref,
            **kwargs,
        )

    client = ctx.obj["client"]
    logger.info("sending workflow request to api")
    with api_client_exception_handler():
        workflow = client.workflow(run_req, workspace_specs, github_specs)

    utf8 = ctx.obj["utf8"]
    click.echo(with_emoji("💫", "Casting workflow #{}".format(workflow.id) + ellipses(utf8), utf8))
    if not local:
        if background:
            click.echo("View logs with `spell logs {}`".format(workflow.managing_run.id))
        else:
            click.echo(with_emoji("✨", "Following workflow at run {}.".format(workflow.managing_run.id), utf8))
            click.echo(with_emoji("✨", "Stop viewing logs with ^C", utf8))
            ctx.invoke(logs, run_id=str(workflow.managing_run.id), follow=True, verbose=verbose)
    else:
        os.environ["SPELL_WORKFLOW_ID"] = str(workflow.id)
        os.system(" ".join(("'{}'".format(x) for x in (command,) + args)))


@workflow.command(name="rm", short_help="Archive a workflow")
@click.argument("workflow_id")
@click.pass_context
def archive(ctx, workflow_id):
    """

    Archive a workflow run specified by WORKFLOW-ID.

    """

    client = ctx.obj["client"]

    with api_client_exception_handler():
        logger.info("Archiving workflow {}".format(workflow_id))
        client.archive_workflow(workflow_id)
    click.echo("Archiving workflow {}.".format(workflow_id))


@workflow.command(
    name="kill",
    short_help="Kill Workflow",
    docs="https://spell.ml/docs/workflow_overview/#interrupting-a-workflow",
)
@click.argument("workflow_id")
@click.pass_context
def kill(ctx, workflow_id):
    """

    Kill a workflow run specified by WORKFLOW-ID.

    This will kill all the runs created by workflow including the managing and child.

    Cannot kill --local workflow runs

    """

    client = ctx.obj["client"]

    with api_client_exception_handler():
        client.kill_workflow(workflow_id)
    click.echo("Succesfully killed workflow {}.".format(workflow_id))


@workflow.command(
    name="stop",
    short_help="Stop Workflow",
    docs="https://spell.ml/docs/workflow_overview/#interrupting-a-workflow",
)
@click.argument("workflow_id")
@click.pass_context
def stop(ctx, workflow_id):
    """

    Stop a workflow run specified by WORKFLOW-ID.

    This will stop all in progress runs and cancel all queued runs for workflow.

    Cannot stop --local workflow runs

    """

    client = ctx.obj["client"]

    with api_client_exception_handler():
        client.stop_workflow(workflow_id)
    click.echo(
        "Stopping workflow {}. Use 'spell logs -f {}' to view logs while the "
        "job finishes..".format(workflow_id, workflow_id)
    )
