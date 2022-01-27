import os
from pathlib import Path
import subprocess
import time
import webbrowser

import click
from halo import Halo
import yaml

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_CONFIG,
)
from spell.cli.commands.keys import maybe_write_private_ssh_key_to_disk
from spell.cli.utils import (
    tabulate_rows,
    format_multiline_table_output,
    format_multiline_text_to_table,
    convert_to_local_time,
    with_emoji,
    git_utils,
    ellipses,
    parse_utils,
    prettify_time,
    require_install,
    get_star_spinner_frames,
    try_add_known_host,
)
from spell.cli.log import logger
from spell.cli.utils import cluster_utils
from spell.cli.utils import group, write_rows
from spell.cli.utils.command_options import (
    dependency_params,
    workspace_spec_params,
    cli_params,
    description_param,
    mount_params,
    download_metrics_params,
    RESOURCE_SPECIFICATION_HELP,
)
from spell.cli.utils.parse_utils import validate_attached_resources, validate_download_dest
from spell.api.models import (
    BatchingConfig,
    ModelServerUpdateRequest,
    ModelServerCreateRequest,
    ModelServerModel,
)
from spell.shared.parse_utils import parse_model_versions, validate_server_name
from spell.shared.servers import (
    create_batching_config,
    create_environment,
    create_pod_autoscale_config,
    create_resource_requirements,
    make_modelserver_update_request,
)
from spell.shared.dependencies import InvalidDependencyConfig

RM_MAX_WAIT_TIME_S = 300
RM_CHECK_PERIOD_S = 5
RM_TOTAL_CHECKS = int(RM_MAX_WAIT_TIME_S / RM_CHECK_PERIOD_S)


@group(
    help="Manage model servers",
    docs="https://spell.ml/docs/model_servers/",
)
@click.option("--raw", help="display output in raw format", is_flag=True, default=False, hidden=True)
@click.pass_context
@cluster_utils.pass_cluster
def server(ctx, cluster, raw):
    if not cluster.get("serving_cluster_name"):
        raise ExitException(
            "A kube-cluster must be created before serving models; try running `spell kube-cluster create`"
        )


@server.command(name="list", short_help="List all your model servers")
@click.pass_context
@click.option("--raw", help="display output in raw format", is_flag=True, default=False, hidden=True)
def list_servers(ctx, raw):
    client = ctx.obj["client"]
    list_model_servers(client, raw)


def with_autoscaler_options(with_defaults=True):
    def decorator(f):
        f = click.option(
            "--target-cpu-utilization",
            type=float,
            help="If average pod CPU usage goes higher than this times the cpu-request the autoscaler "
            "will spin up a new pod.",
        )(f)
        f = click.option(
            "--target-requests-per-second",
            type=float,
            help="The autoscaler will scale up pods if the average number of HTTP(S) requests per second "
            "to a pod exceeds this value.",
        )(f)
        f = click.option(
            "--max-pods",
            type=int,
            default=5 if with_defaults else None,
            help="The autoscaler will never scale to more pods than this.",
        )(f)
        return click.option(
            "--min-pods",
            type=int,
            default=1 if with_defaults else None,
            help="The autoscaler will never scale to fewer pods than this.",
        )(f)

    return decorator


def with_resource_requirements_options(with_defaults=True):
    def decorator(f):
        f = click.option(
            "--gpu-limit",
            type=int,
            help=("Maximum number of GPUs allowable to each pod. " "This defaults to 1 if the node group has GPUs"),
        )(f)
        f = click.option(
            "--ram-limit",
            type=int,
            help="The maximum amount of RAM a pod can use in MB. It will be terminated if it exceeds this.",
        )(f)
        f = click.option(
            "--ram-request",
            type=int,
            help="The amount of RAM you expect each pod to use in MB",
        )(f)
        f = click.option("--cpu-limit", type=float, help="The maximum amount of vCPU cores a pod can use")(f)
        return click.option(
            "--cpu-request",
            type=float,
            default=0.9 if with_defaults else None,
            help="The amount of vCPU cores you expect each pod to use",
        )(f)

    return decorator


def with_batching_options(f):
    f = click.option(
        "--request-timeout",
        type=int,
        help=(
            "The maximum amount of time in milliseconds to wait before processing a request. "
            "Default is {}ms. By using this flag, you will enable batching.".format(
                BatchingConfig.DEFAULT_REQUEST_TIMEOUT
            )
        ),
    )(f)
    return click.option(
        "--max-batch-size",
        type=int,
        help=(
            "The maximum batch size. Default is {}. ".format(BatchingConfig.DEFAULT_MAX_BATCH_SIZE)
            + "By using this flag, you will enable batching."
        ),
    )(f)


def list_model_servers(client, raw):
    with api_client_exception_handler():
        model_servers = client.get_model_servers()
    if len(model_servers) == 0:
        click.echo("There are no model servers to display.")
    else:

        data = [
            (
                ms.server_name,
                ms.url,
                get_display_status(ms),
                ms.get_age(),
            )
            for ms in model_servers
        ]
        tabulate_rows(data, headers=["NAME", "URL", "PODS (READY/TOTAL)", "AGE"], raw=raw)


def get_display_status(model_server):
    if model_server.status not in ("running"):
        return model_server.status.capitalize()

    runningPods = [p for p in model_server.pods if not p.deleted_at]
    return f"{len([p for p in runningPods if p.ready_at])}/{len(runningPods)}"


@server.command(
    name="serve",
    short_help="Create a new model server",
    help="""Create a new model server using an entrypoint
            to a Python predictor and zero or more models.""",
    docs="https://spell.ml/docs/model_servers/#creating-model-servers",
)
@click.argument("models", metavar="MODEL:VERSION", nargs=-1)
@click.argument("entrypoint")
@click.option(
    "--name",
    help="Name of the model server. Defaults to the model name if only one model is provided",
)
@click.option(
    "--config",
    type=click.File(),
    help="Path to a YAML for JSON file which will be passed through to the Predictor",
)
@click.option(
    "--node-group",
    help="Node group to schedule the server to. Defaults to initial node group.",
)
@click.option(
    "--classname",
    help="Name of the Predictor class to use. Only required if more than one predictor exist in the Python module used",
)
@dependency_params(include_docker=False, resource_type="model server")
@workspace_spec_params
@description_param(resource_type="model server")
@cli_params
@mount_params
@with_autoscaler_options()
@with_resource_requirements_options()
@click.option(
    "--num-processes",
    type=int,
    help=(
        "The number of processes to run the model server on. "
        "By default this is (2 * numberOfCores) + 1 or equal to the available GPUs if applicable"
    ),
)
@click.option(
    "--enable-batching",
    is_flag=True,
    help=(
        "Enable server-side batching. "
        "Without specifying further options this enables batching with the default options"
    ),
)
@with_batching_options
@click.option(
    "--validate",
    is_flag=True,
    help="Validate the structure of your predictor class. All Python packages required to import"
    " your predictor must be in your Python environment",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Launch the server in debug mode. For security purposes, this should not be used in production",
)
@click.option(
    "--open/--no-open",
    "open_server_webpage",
    default=True,
    help="Open the server's webpage in a browser after creation",
)
@click.pass_context
def serve(
    ctx,
    models,
    entrypoint,
    name,
    config,
    node_group,
    classname,
    github_url,
    github_ref,
    python_env_deps,
    pip_packages,
    requirements_file,
    apt_packages,
    conda_file,
    commit_ref,
    description,
    envvars,
    force,
    verbose,
    raw_resources,
    min_pods,
    max_pods,
    target_cpu_utilization,
    target_requests_per_second,
    cpu_request,
    cpu_limit,
    ram_request,
    ram_limit,
    gpu_limit,
    num_processes,
    enable_batching,
    max_batch_size,
    request_timeout,
    debug,
    validate,
    open_server_webpage,
    **kwargs,
):
    model_versions = parse_model_versions(models)
    if name is None:
        if len(model_versions) == 0:
            raise ExitException("A server name must be provided with --name if not using a model")
        elif len(model_versions) == 1:
            name = model_versions[0][0]
        else:
            raise ExitException("A server name must be provided with --name when using multiple models")
    if github_url and validate:
        raise ExitException("Cannot use --validate with --github-url")
    config = read_config(config)

    maybe_write_private_ssh_key_to_disk(ctx)
    try_add_known_host(ctx)

    server_req = make_modelserver_create_request(
        ctx,
        model_versions,
        entrypoint,
        name,
        config,
        node_group,
        classname,
        python_env_deps,
        pip_packages,
        requirements_file,
        conda_file,
        apt_packages,
        commit_ref,
        description,
        envvars,
        force,
        verbose,
        github_url,
        github_ref,
        raw_resources,
        min_pods,
        max_pods,
        target_cpu_utilization,
        target_requests_per_second,
        cpu_request,
        cpu_limit,
        ram_request,
        ram_limit,
        gpu_limit,
        num_processes,
        enable_batching,
        max_batch_size,
        request_timeout,
        debug,
        validate,
        **kwargs,
    )
    client = ctx.obj["client"]
    logger.info("sending model server request to api")
    with api_client_exception_handler():
        server = client.new_model_server(server_req)

    utf8 = ctx.obj["utf8"]
    click.echo(with_emoji("💫", "Starting server {}".format(server.server_name), utf8) + ellipses(utf8))
    if open_server_webpage:
        url = "{}/web_redirect/{}/model-servers/{}".format(
            ctx.obj["client_args"]["base_url"], ctx.obj["owner"], server.server_name
        )
        webbrowser.open(url)


def make_modelserver_create_request(
    ctx,
    model_versions,
    entrypoint,
    name,
    config,
    node_group,
    classname,
    python_env_deps,
    pip_packages,
    requirements_file,
    conda_file,
    apt_packages,
    commit_ref,
    description,
    envvars,
    force,
    verbose,
    github_url,
    github_ref,
    raw_resources,
    min_pods,
    max_pods,
    target_cpu_utilization,
    target_requests_per_second,
    cpu_request,
    cpu_limit,
    ram_request,
    ram_limit,
    gpu_limit,
    num_processes,
    enable_batching,
    max_batch_size,
    request_timeout,
    debug,
    validate,
    **kwargs,
):
    repo = git_utils.detect_repo(
        ctx,
        github_url=github_url,
        github_ref=github_ref,
        force=force,
        description=description,
        commit_ref=commit_ref,
        allow_missing=False,
        resource_type="model server",
    )
    if github_url is None and entrypoint is not None:
        validate_entrypoint(repo, entrypoint)
        entrypoint = git_utils.get_tracked_repo_path(repo, entrypoint)
    if validate:
        validate_predictor(entrypoint, repo, classname=classname)
    try:
        curr_envvars = parse_utils.parse_env_vars(envvars)
        environment = create_environment(
            python_env_deps,
            pip_packages,
            requirements_file,
            conda_file,
            apt_packages,
            curr_envvars,
        )
    except ValueError as e:
        raise ExitException(str(e))
    except InvalidDependencyConfig as e:
        raise ExitException(e.message, SPELL_INVALID_CONFIG)
    attached_resources = validate_attached_resources(raw_resources)
    pod_autoscale_config = create_pod_autoscale_config(
        min_pods, max_pods, target_cpu_utilization, target_requests_per_second
    )
    resource_requirements = create_resource_requirements(
        ram_request,
        cpu_request,
        ram_limit,
        cpu_limit,
        gpu_limit,
    )
    batching_config = create_batching_config(enable_batching, max_batch_size, request_timeout)

    return ModelServerCreateRequest(
        models=[ModelServerModel(model_name=m[0], version_id=m[1], version_name=m[2]) for m in model_versions],
        server_name=name,
        config=config,
        node_group=node_group,
        entrypoint=entrypoint,
        predictor_class=classname,
        environment=environment,
        attached_resources=attached_resources,
        description=repo.description,
        repository=repo,
        pod_autoscale_config=pod_autoscale_config,
        resource_requirements=resource_requirements,
        num_processes=num_processes,
        batching_config=batching_config,
        debug=debug,
    )


def validate_entrypoint(repo, entrypoint):
    entrypoint = git_utils.get_tracked_repo_path(repo, entrypoint)
    if entrypoint is None:
        raise ExitException(
            "ENTRYPOINT must be a path within the repository.",
            SPELL_INVALID_CONFIG,
        )
    if not os.path.isfile(entrypoint):
        raise ExitException(f"ENTRYPOINT {entrypoint} file not found.", SPELL_INVALID_CONFIG)


@server.command(
    name="rm",
    short_help="Remove a model server",
    help="""Remove the model server with the specified NAME""",
    docs="https://spell.ml/docs/model_servers/#stopping-or-deleting-model-servers",
)
@click.pass_context
@click.argument("server-name")
@click.option("-f", "--force", is_flag=True, help="Remove the server even if it is running")
def remove(ctx, server_name, force):
    validate_server_name(server_name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        ms = client.get_model_server(server_name=server_name)
    spinner = None
    is_utf8_enabled = ctx.obj["utf8"]
    if ctx.obj["interactive"]:
        spinner = Halo(spinner=get_star_spinner_frames(is_utf8_enabled))
    if ms.status not in ("stopping", "stopped", "failed"):
        if not force:
            raise ExitException("Model server must be stopped before it can be removed")
        with api_client_exception_handler():
            client.stop_model_server(server_name=server_name)
        ms.status = "stopping"
    if ms.status == "stopping":
        waiting_text = f"Waiting for server {server_name} to complete stopping..."
        if spinner:
            spinner.text = waiting_text
            spinner.start()
        else:
            click.echo(waiting_text)
        is_stopped = False
        for _ in range(RM_TOTAL_CHECKS):
            with api_client_exception_handler():
                ms = client.get_model_server(server_name=server_name)
            if ms.status == "stopped":
                is_stopped = True
                break
            time.sleep(RM_CHECK_PERIOD_S)
        if not is_stopped:
            if spinner:
                spinner.stop()
            raise ExitException(
                f"Model server is still not stopped after {RM_MAX_WAIT_TIME_S} seconds. Try again later"
            )
    with api_client_exception_handler():
        client.delete_model_server(server_name=server_name)
    removed_text = f"Successfully removed model server {server_name}"
    if spinner:
        spinner.stop_and_persist(text=f"Successfully removed model server {server_name}", symbol="🎉")
    else:
        click.echo(with_emoji("🎉", removed_text, is_utf8_enabled))


@server.command(
    name="start",
    short_help="Start a model server",
    help="""Start the model server with the specified SERVER-NAME""",
)
@click.pass_context
@click.argument("server-name")
def start(ctx, server_name):
    validate_server_name(server_name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.start_model_server(server_name=server_name)
    click.echo(f"Successfully started model server {server_name}")


@server.command(
    name="stop",
    short_help="Stop a model server",
    help="""Stop the model server with the specified SERVER-NAME""",
    docs="https://spell.ml/docs/model_servers/#stopping-or-deleting-model-servers",
)
@click.pass_context
@click.argument("server-name")
def stop(ctx, server_name):
    validate_server_name(server_name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.stop_model_server(server_name=server_name)
    click.echo(f"Successfully began stopping model server {server_name}")


@server.command(docs="https://spell.ml/docs/model_servers/#updating-model-servers")
@click.argument("server-name")
@click.option(
    "--model",
    "models",
    metavar="NAME:VERSION",
    multiple=True,
    help="A new model to attach. This overwrites any existing models on the model server. "
    "For example, if a server is using ModelA, and --model ModelB --model ModelB is entered, "
    "the server will use both ModelA and ModelB, but if only --model ModelB is specified, "
    "the server will only use ModelB. See the spell server models command group for more options.",
)
@click.option("--entrypoint", help="Choose a new entrypoint for the server")
@click.option(
    "--update-repo",
    is_flag=True,
    default=False,
    help="Sync the server with the HEAD of the currently active repository.",
)
@click.option(
    "--config",
    type=click.File(),
    help="Path to a YAML for JSON file which will be passed through to the Predictor",
)
@click.option(
    "--node-group",
    help="Node group to schedule the server to. Defaults to initial node group.",
)
@click.option(
    "--classname",
    help="Name of the Predictor class to use. "
    "Only required if more than one predictor exists in the Python module used",
)
@dependency_params(include_docker=False, resource_type="model server")
@workspace_spec_params
@click.option(
    "--update-spell-version",
    "update_spell_version",
    is_flag=True,
    default=False,
    help="Update the version of Spell python code running the model server and "
    "the version of the Spell docker image it runs on",
)
@description_param(resource_type="model server")
@cli_params
@mount_params
@with_autoscaler_options(with_defaults=False)
@with_resource_requirements_options(with_defaults=False)
@click.option(
    "--num-processes",
    help=(
        "The number of processes to run the model server on. By default this is (2 * numberOfCores) + 1"
        ' or equal to the number of available GPUs if applicable. To use the default, enter "default"'
    ),
)
@click.option(
    "--enable-batching/--disable-batching",
    "batching_flag",
    default=None,
    help="Enable or disable server-side batching",
)
@with_batching_options
@click.option(
    "--validate",
    is_flag=True,
    help="Validate the structure of your predictor class. All Python packages required to import"
    " your Predictor must be in your Python environment",
)
@click.option(
    "--debug-on/--debug-off",
    "debug",
    default=None,  # This default makes it a three-way flag
    help="Launch the server in debug mode. For security purposes, this should not be used in production",
)
@click.pass_context
def update(ctx, server_name, **kwargs):
    """Update a custom model server"""
    if kwargs["commit_ref"] == "HEAD" and not any(v or v == 0 for k, v in kwargs.items() if k != "commit_ref"):
        raise ExitException("At least one option must be specified to update a model server")
    if kwargs["max_batch_size"] and not kwargs["request_timeout"]:
        raise ExitException("--request-timeout must be specified if --max-batch-size is provided")
    if not kwargs["max_batch_size"] and kwargs["request_timeout"]:
        raise ExitException("--max-batch-size must be specified if --request-timeout is provided")
    if kwargs["github_url"] and kwargs["validate"]:
        raise ExitException("Cannot use --validate with --github-url")
    if kwargs["validate"] and not kwargs["entrypoint"]:
        raise ExitException("Cannot use --validate without --entrypoint")

    kwargs["models"] = parse_model_versions(kwargs["models"]) if kwargs["models"] else None
    kwargs["config"] = read_config(kwargs["config"])
    if kwargs["update_repo"] and any(
        (
            kwargs["github_url"],
            kwargs["github_ref"],
            kwargs["entrypoint"],
            kwargs["commit_ref"] != "HEAD",
        )
    ):
        click.echo(
            "--update-repo is not needed when explicitly using --github-url, --github-ref, "
            "--commit-ref, or --entrypoint. Ignoring."
        )
        kwargs["update_repo"] = False

    maybe_write_private_ssh_key_to_disk(ctx)
    try_add_known_host(ctx)

    kwargs["repo"] = None
    if any(
        (
            kwargs["github_url"],
            kwargs["github_ref"],
            kwargs["commit_ref"] != "HEAD",
            kwargs["entrypoint"],
            kwargs["update_repo"],
        )
    ):
        repo = git_utils.detect_repo(
            ctx,
            github_url=kwargs["github_url"],
            github_ref=kwargs["github_ref"],
            force=kwargs["force"],
            description=kwargs["description"],
            commit_ref=kwargs["commit_ref"],
            allow_missing=False,
            resource_type="model server",
        )
        repo.description = None
        if kwargs["github_url"] is None and kwargs["entrypoint"] is not None:
            kwargs["entrypoint"] = git_utils.get_tracked_repo_path(repo, kwargs["entrypoint"])
            validate_entrypoint(repo, kwargs["entrypoint"])
        if kwargs["validate"]:
            validate_predictor(kwargs["entrypoint"], repo, classname=kwargs["classname"])
        kwargs["repo"] = repo
    kwargs["envvars"] = parse_utils.parse_env_vars(kwargs["envvars"])
    kwargs["attached_resources"] = validate_attached_resources(kwargs["raw_resources"])
    try:
        server_req = make_modelserver_update_request(**kwargs)
    except ValueError as e:
        raise ExitException(str(e))
    except InvalidDependencyConfig as e:
        raise ExitException(e.message, SPELL_INVALID_CONFIG)
    client = ctx.obj["client"]
    logger.info("sending model server update request to api")
    with api_client_exception_handler():
        client.update_model_server(server_name, server_req)

    utf8 = ctx.obj["utf8"]
    click.echo(with_emoji("💫", f"Updating server {server_name}", utf8) + ellipses(utf8))


def get_grafana_link(kubernetes_name, serving_cluster_domain):
    prometheus_query_prefill = (
        '"sum%20by%20(spell_metric_name,%20spell_tag)%20(%7Bser'
        f'vice%3D%5C"{kubernetes_name}%5C",%20spell_metric_name!%3D%5C%22%5C%22%7D)"%7D,'
        '%7B"ui":%5Btrue,true,true,"none"%5D%7D%5D'
    )
    query_string_template = f'orgId=1&left=%5B"now-1h","now","",%7B"expr":{prometheus_query_prefill}'
    return f"https://{serving_cluster_domain}/grafana/explore?{query_string_template}"


@server.group(
    "mounts",
    help="Modify a server's mounts",
    docs="https://spell.ml/docs/model_servers/#managing-model-server-mounts",
)
@click.pass_context
def mounts_group(_ctx):
    pass


@mounts_group.command(
    "add",
    short_help="Add mounts to a server",
    help="""Add mounts to a server

    Attach resource files or directories (e.g. from a run output, public dataset, or upload)
    {resource_spec}
    """.format(
        resource_spec=RESOURCE_SPECIFICATION_HELP
    ),
    docs="https://spell.ml/docs/model_servers/#managing-model-server-mounts",
)
@click.argument("server-name")
@click.argument("mounts", nargs=-1)
@click.pass_context
def add_mounts(ctx, server_name, mounts):
    if not mounts:
        raise ExitException("At least one mount must be specified")
    client = ctx.obj["client"]
    existing_resources = get_additional_resources(client, server_name)
    new_resources = validate_attached_resources(mounts)
    result_resources = existing_resources.copy()
    for src, dest in new_resources.items():
        if src not in existing_resources or existing_resources[src] != dest:
            result_resources[src] = dest
        else:
            click.echo(f"Mount {src} at {dest} already exists!")
    if existing_resources != result_resources:
        update_server_additional_resources(client, server_name, result_resources, ctx.obj["utf8"])
    else:
        click.echo("No changes to mounts required")


@mounts_group.command(
    "rm",
    short_help="Remove a server's mounts",
    docs="https://spell.ml/docs/model_servers/#managing-model-server-mounts",
)
@click.argument("server-name")
@click.argument("mounts", nargs=-1)
@click.pass_context
def rm_mounts(ctx, server_name, mounts):
    """Remove a server's mounts

    Remove resource files or directories (e.g. from a run output, public dataset, or upload).
    The resource (specified by a Spell resource path) is required, but the mount path is not.
    """
    if not mounts:
        raise ExitException("At least one mount must be specified")
    client = ctx.obj["client"]
    existing_resources = get_additional_resources(client, server_name)
    if not existing_resources:
        click.echo("No changes to mounts required")
        return
    removed_resources = validate_attached_resources(mounts)
    result_resources = existing_resources.copy()
    for src in removed_resources:
        if src in existing_resources:
            result_resources.pop(src)
        else:
            click.echo(f"{src} is not mounted!")
    utf8 = ctx.obj["utf8"]
    if existing_resources != result_resources:
        if result_resources:
            update_server_additional_resources(client, server_name, result_resources, utf8)
        else:
            with api_client_exception_handler():
                client.delete_model_server_mounts(server_name)
            print_mount_update_message(server_name, utf8)
    else:
        click.echo("No changes to nounts required")


def get_additional_resources(client, server_name):
    validate_server_name(server_name)
    with api_client_exception_handler():
        ms = client.get_model_server(server_name=server_name)
    existing_resources = {}
    for key, value in ms.additional_resources.items():
        if value.startswith("/mounts/"):
            existing_resources[key] = value[8:]  # strip /mounts/
        else:
            existing_resources[key] = value
    return existing_resources


def update_server_additional_resources(client, server_name, additional_resources, utf8):
    request = ModelServerUpdateRequest(attached_resources=additional_resources)
    with api_client_exception_handler():
        client.update_model_server(server_name, request)
    print_mount_update_message(server_name, utf8)


def print_mount_update_message(server_name, utf8):
    click.echo(with_emoji("💫", f"Updating mounts for server {server_name}", utf8) + ellipses(utf8))


@server.group(
    "models",
    help="Add or remove models from a model server",
    docs="https://spell.ml/docs/model_servers/#advanced-serving-multiple-models",
)
@click.pass_context
def models_group(ctx):
    pass


@models_group.command(
    "add",
    help="Add models to a model server",
    docs="https://spell.ml/docs/model_servers/#advanced-serving-multiple-models",
)
@click.argument("server-name")
@click.argument("models", nargs=-1)
@click.pass_context
def add_models(ctx, server_name, models):
    if not models:
        raise ExitException("At least one model must be specified")
    validate_server_name(server_name)
    # Parsed models is a tuple of (model_name, id(optional), tag(optional))
    parsed_models = set(parse_model_versions(models))
    client = ctx.obj["client"]
    with api_client_exception_handler():
        ms = client.get_model_server(server_name=server_name)
    # Using None here because you can't specify both tag and id in request
    existing_models = {(m.model_name, m.id, None) for m in ms.model_versions}
    existing_model_lookup = {m.model_name: m for m in ms.model_versions}
    new_models = set(existing_models)
    for model in parsed_models:
        model_name = model[0]
        if model_name not in existing_model_lookup:
            new_models.add(model)
        else:
            existing_model = existing_model_lookup[model_name]
            if (model[1] and model[1] != existing_model.id) or (model[2] and model[2] != existing_model.version):
                raise ExitException(
                    f"Cannot use two versions of the same model {model_name}. "
                    f"Already found version {existing_model.formatted_version}. "
                    "To update a model version, use the spell server update command."
                )
            else:
                raise ExitException(
                    f"Model {model_name}:{existing_model.formatted_version} "
                    f"is already attached to server {server_name}."
                )

    new_models = [ModelServerModel(model_name=m[0], version_id=m[1], version_name=m[2]) for m in new_models]
    req = ModelServerUpdateRequest(models=new_models)
    with api_client_exception_handler():
        client.update_model_server(server_name, req)
        utf8 = ctx.obj["utf8"]
        click.echo(
            with_emoji(
                "💫",
                f"Adding {len(models)} models to model server {server_name}",
                utf8,
            )
            + ellipses(utf8)
        )


@models_group.command(
    "rm",
    short_help="Remove models from a model server",
    help="Remove models from a model server. Only the name of the model name is required",
    docs="https://spell.ml/docs/model_servers/#advanced-serving-multiple-models",
)
@click.argument("server-name")
@click.argument("models", nargs=-1)
@click.pass_context
def rm_models(ctx, server_name, models):
    if not models:
        raise ExitException("At least one model must be specified")
    validate_server_name(server_name)
    if not models:
        click.echo("No models specified to remove. Nothing to do.")
        return
    parsed_models = []
    for model in models:
        model_name, _, _ = model.partition(":")
        parsed_models.append(model_name)
    parsed_models = set(parsed_models)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        ms = client.get_model_server(server_name=server_name)
    if not ms.model_versions:
        click.echo("Server has no models to remove. Nothing to do")
        return
    existing_models = {m.model_name: (m.id, m.version) for m in ms.model_versions}
    new_models = dict(existing_models)
    for model in parsed_models:
        existing_model = existing_models.get(model, None)
        if existing_model:
            new_models.pop(model, None)
        else:
            raise ExitException(f"Server {server_name} doesn't have model {model}.")

    with api_client_exception_handler():
        if not new_models:
            click.echo(f"Removing all {len(existing_models)} models from server {server_name}")
            client.delete_model_server_models(server_name)
        else:
            new_models = [
                ModelServerModel(model_name=model, version_id=version[0]) for model, version in new_models.items()
            ]
            req = ModelServerUpdateRequest(models=new_models)
            client.update_model_server(server_name, req)
            utf8 = ctx.obj["utf8"]
            click.echo(
                with_emoji(
                    "💫",
                    f"Removing {len(existing_models) - len(new_models)} models from server {server_name}",
                    utf8,
                )
                + ellipses(utf8)
            )


@server.command(
    short_help="Describe a model server",
    help="""Describe a model server with the specified SERVER-NAME""",
)
@click.pass_context
@click.argument("server-name")
def describe(ctx, server_name):
    validate_server_name(server_name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        ms = client.get_model_server(server_name=server_name)
    lines = [("Server Name", ms.server_name)]
    lines.extend(get_custom_model_server_info_lines(ms))
    lines.append(("Date Created", convert_to_local_time(ms.created_at)))
    lines.append(("Time Running", ms.get_age()))
    lines.append(("URL", ms.url))
    if ms.node_group_name:
        lines.append(("Node Group", ms.node_group_name))
    lines.append(("Server ID", ms.id))
    lines.append(
        (
            "Grafana Link",
            get_grafana_link(ms.kubernetes_name, ms.cluster.get("serving_cluster_domain", "")),
        )
    )
    if not ms.cluster.get("is_serving_cluster_public", False):
        lines.append(("*NOTE*", "This will only be accessible within the same VPC of the cluster"))
    if len(ms.additional_resources) > 0:
        lines.extend(
            format_multiline_table_output(
                "Mounts",
                ms.additional_resources,
                lambda resource, destination: f"{resource} at {destination}",
            )
        )
    if ms.environment:
        lines.extend(get_model_server_env_lines(ms.environment))
    click.echo("Server Info:")
    tabulate_rows(lines)
    lines = [("Pods (Ready/Total)", get_display_status(ms))]
    if ms.resource_requirements:
        request = ms.resource_requirements.request
        limit = ms.resource_requirements.limit
        if request and request.cpu_millicores:
            lines.append(("CPU Request", f"{request.cpu_millicores}m"))
        if limit and limit.cpu_millicores:
            lines.append(("CPU Limit", f"{limit.cpu_millicores}m"))
        if request and request.memory_mebibytes:
            lines.append(("Memory Request", f"{request.memory_mebibytes} MiB"))
        if limit and limit.memory_mebibytes:
            lines.append(("Memory Limit", f"{limit.memory_mebibytes} MiB"))

    if ms.pod_autoscale_config:
        config = ms.pod_autoscale_config
        if config.min_pods:
            lines.append(("Min Pods", config.min_pods))
        if config.max_pods:
            lines.append(("Max Pods", config.max_pods))
        if config.target_cpu_utilization:
            lines.append(("Target Pod CPU", f"{config.target_cpu_utilization}%"))
        if config.target_avg_requests_per_sec_millicores:
            lines.append(
                (
                    "Target Req per Second",
                    str(config.target_avg_requests_per_sec_millicores / 1000),
                )
            )
    if ms.num_processes is not None:
        lines.append(("Number of Worker Processes", ms.num_processes))
    lines.extend(get_batching_config_lines(ms.batching_config))

    click.echo("\nPerformance Info:")
    tabulate_rows(lines)


def get_custom_model_server_info_lines(ms):
    lines = []
    if ms.model_versions:
        lines.extend(
            format_multiline_table_output(
                "Models",
                ms.model_versions,
                formatter=lambda mv: f"{mv.specifier} ({mv.resource})",
            )
        )
    lines.append(("Status", ms.status.title()))
    if ms.workspace:
        lines.append(("Repository", ms.workspace.name))
    if ms.github_url:
        lines.append(("GitHub URL", ms.github_url))
    if ms.debug:
        lines.append(("Debug", ms.debug))
    if ms.git_commit_hash:
        formatted_hash = ms.git_commit_hash
        if ms.has_uncommitted:
            formatted_hash += "[Uncommitted]"
        lines.append(("GitCommitHash", formatted_hash))
    if ms.entrypoint:
        lines.append(("Entrypoint", ms.entrypoint))
    if ms.predictor_class:
        lines.append(("Predictor Class", ms.predictor_class))
    return lines


def get_model_server_env_lines(environment):
    lines = []
    if environment.apt:
        lines.extend(format_multiline_table_output("Apt", environment.apt))
    # TODO(Justin) pip_strings and pip_env_strings should be removed in 0.47.0
    if environment.pip_env:
        lines.extend(format_multiline_table_output("Python Environment", environment.pip_env))
    elif environment.pip_env_strings:
        lines.extend(format_multiline_table_output("Python Environment", environment.pip_env_strings))
    if environment.requirements_file:
        lines.extend(format_multiline_text_to_table("Requirements File", environment.requirements_file))
    if environment.pip:
        lines.extend(format_multiline_table_output("Pip", environment.pip))
    elif environment.pip_strings:
        lines.extend(format_multiline_table_output("Pip", environment.pip_strings))
    if environment.env_vars:
        lines.extend(format_multiline_table_output("Environment Vars", environment.env_vars))
    if environment.conda_file:
        lines.append(("Conda File", environment.conda_file))
    return lines


def get_batching_config_lines(config):
    lines = []
    if config and config.is_enabled:
        lines.append(("Batching Enabled", "Yes"))
        lines.append(("Batch Timeout", f"{config.request_timeout_ms}ms"))
        lines.append(("Max Batch Size", config.max_batch_size))
    else:
        lines.append(("Batching Enabled", "No"))
    return lines


@server.command(name="status", help="Get the status of all pods for this server.")
@click.pass_context
@click.argument("server-name")
def status(ctx, server_name):
    validate_server_name(server_name)
    with api_client_exception_handler():
        ms = ctx.obj["client"].get_model_server(server_name=server_name)
    print_pod_statuses(ms)


def print_pod_statuses(model_server):
    rows = []
    for p in model_server.pods:
        ready_at = prettify_time(p.ready_at) if p.ready_at else "-"
        rows.append([p.id, prettify_time(p.created_at), ready_at])
    tabulate_rows(rows, headers=["POD ID", "CREATED AT", "READY AT"])


@server.command(
    name="logs",
    short_help="Get logs from a model server",
    help="""Get logs for the model server with the specified SERVER-NAME""",
    docs="https://spell.ml/docs/model_servers/#viewing-model-server-logs",
)
@click.pass_context
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("-p", "--pod", help="The ID of the pod you would like logs for. Omit to get a list of all pods.")
@click.argument("server-name")
def logs(ctx, server_name, pod, follow):
    validate_server_name(server_name)
    client = ctx.obj["client"]

    # Prompt with all pods so user can select one
    if not pod:
        with api_client_exception_handler():
            ms = client.get_model_server(server_name=server_name)
        if len(ms.pods) == 0:
            click.echo("There are no active pods for this server.")
            return
        if len(ms.pods) == 1:
            pod = str(ms.pods[0].id)
        else:
            print_pod_statuses(ms)
            pod_ids = [str(pod.id) for pod in ms.pods]
            pod = click.prompt("Enter the ID of the pod you would like logs for", type=click.Choice(pod_ids))

    utf8 = ctx.obj["utf8"]
    with api_client_exception_handler():
        try:
            for entry in client.get_model_server_log_entries(server_name, pod, follow=follow):
                click.echo(entry.log)
        except KeyboardInterrupt:
            if follow:
                click.echo()
                click.echo(
                    with_emoji(
                        "✨",
                        "Use 'spell model-servers logs -f {}' to view logs again".format(server_name),
                        utf8,
                    )
                )


@server.command(short_help="cURL the predict URL of a model server")
@require_install("curl")
@click.argument("server-name")
@click.argument("curl_args", nargs=-1)
@click.option(
    "--json",
    "json_arg",
    help="Pass a json object to the predict URL. If a path to a file is provided, it will be read and passed",
)
@click.pass_context
def predict(ctx, server_name, curl_args, json_arg):
    """Issue a cURL command against the predict endpoint of a model server

    This is a POST request. Further cURL arguments can be provided using "--". Example:
    spell server predict myserver -- -H "Content-Type: appliation/json" -d '{data: [1,2,3]}'
    """
    cmd = ["curl", "-X", "POST"]
    if json_arg:
        cmd.extend(["-H", "Content-Type: application/json", "-d"])
        json_file = Path(json_arg)
        if json_file.exists():
            cmd.append("@" + json_arg)
        else:
            cmd.append(json_arg)
    validate_server_name(server_name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        server = client.get_model_server(server_name=server_name)
    cmd.extend(curl_args)
    cmd.append(server.url)
    click.echo(subprocess.check_output(cmd))


@server.command(short_help="cURL the health URL of a model server")
@require_install("curl")
@click.argument("server-name")
@click.argument("curl_args", nargs=-1)
@click.pass_context
def healthcheck(ctx, server_name, curl_args):
    """Issue a cURL command against the health endpoint of a model server

    This is a GET request. Further cURL arguments can be provided using "--". Example:
    spell server healthcheck myserver -- -H "Content-Type: appliation/json" -d '{data: [1,2,3]}'
    """
    validate_server_name(server_name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        server = client.get_model_server(server_name=server_name)
    cmd = ["curl"]
    cmd.extend(curl_args)
    url = server.url[: -len("predict")] + "health"
    cmd.append(url)
    click.echo(subprocess.check_output(cmd))


@server.command(
    name="download-metrics",
    short_help="Download metrics from a model server",
    docs="https://spell.ml/docs/model_servers/",
)
@click.argument("server-name")
@download_metrics_params
@click.pass_context
def download_metrics_server(ctx, server_name, dest, force):
    """
    Download metrics from a model server specified by model server name.
    """
    validate_download_dest(dest, force)
    client = ctx.obj["client"]

    metric_values = []
    with api_client_exception_handler():
        metric_names = client.list_model_server_metric_names(server_name)

    for metric_name in metric_names:
        with api_client_exception_handler():
            server_metrics = client.get_model_server_metric(server_name, metric_name)

        for tagged_subset in server_metrics:
            tag = tagged_subset["tag"]
            metric_values += [[metric_name, tag, idx, value] for (idx, value) in tagged_subset["values"]]

    write_rows(dest, metric_values, header=["index", "metric_name", "tag", "value"])
    click.echo(f"Downloaded metrics to {dest}.")


def get_config_info(config, owner, cluster_name):
    server_name = config["specifier"]
    validate_server_name(server_name)
    owner = owner if "owner" not in config else config["owner"]
    cluster_name = cluster_name if "clusterName" not in config else config["clusterName"]
    return server_name, owner, cluster_name


def read_config(config_file):
    """This function loads, then dumps the config. This both ensures it's valid YAML and
    standardizes the string representation so it can be more easily manipulated.
    """
    if not config_file:
        return ""
    try:
        config = yaml.safe_load(config_file)
        return yaml.dump(config)
    except yaml.scanner.ScannerError:
        raise ExitException("Config file is not valid YAML")


def validate_predictor(entrypoint, repo, classname=None):
    try:
        from spell.serving.api import API
        from spell.serving.exceptions import InvalidPredictor
    except ImportError:
        raise ExitException(
            "Could not import required packages to validate your predictor. "
            "Please run `pip install --upgrade 'spell[serving]'` and rerun this command"
        )
    try:
        API.from_entrypoint(Path(entrypoint), classname=classname, root=Path(repo.local_root))
    except InvalidPredictor as e:
        raise ExitException(str(e))


@server.command(
    name="grafana",
    short_help="Open the model server grafana dashboard",
    help="""Open a model server grafana dashboard in a new tab in your web browser""",
)
@click.pass_context
@click.argument("server-name")
def grafana(ctx, server_name):
    client = ctx.obj["client"]
    with api_client_exception_handler():
        ms = client.get_model_server(server_name=server_name)

    link = get_grafana_link(ms.kubernetes_name, ms.cluster.get("serving_cluster_domain", ""))
    webbrowser.open(link)
