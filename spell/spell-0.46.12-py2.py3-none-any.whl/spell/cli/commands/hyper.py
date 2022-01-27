import click
from datetime import datetime
from dateutil.tz import tzutc

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_CONFIG,
)
from spell.cli.commands.keys import maybe_write_private_ssh_key_to_disk
from spell.cli.commands.run import create_run_request
from spell.cli.log import logger
from spell.cli.utils.command_options import (
    dependency_params,
    workspace_spec_params,
    machine_config_params,
    cli_params,
    description_param,
    idempotent_option,
    project_option,
    timeout_option,
    json_hyper_param_option,
    stop_condition_option,
    tensorboard_params,
    label_param,
    download_metrics_params,
)
from spell.cli.utils.exceptions import ParseException
from spell.cli.utils.parse_utils import (
    parse_list_params,
    parse_random_params,
    parse_bayesian_params,
    parse_conditions,
    validate_download_dest,
)
from spell.cli.utils import (
    tabulate_rows,
    with_emoji,
    ellipses,
    group,
    get_or_create_project,
    prettify_time,
    prettify_timespan,
    write_rows,
    try_add_known_host,
)


def common_hyper_exec_options(func):
    for opt in (
        idempotent_option,
        project_option,
        machine_config_params(exclude_kubernetes=True),
        dependency_params(resource_type="hyperparameter search"),
        workspace_spec_params,
        description_param(resource_type="hyperparameter search"),
        cli_params,
        tensorboard_params,
        label_param,
    ):
        func = opt(func)
    return func


def hyper_exec_args(func):
    # Ordering here is reverse from what might be intuitive. Since
    # click.argument is meant to be used as a decorator, if the decorator
    # is ad-hoc applied to the function they get applied in the "reverse"
    # order. This ordering is required to implement
    #    COMMAND ARGS...
    # syntax as opposed to
    #    ARGS... COMMAND
    # syntax
    func = click.argument("args", nargs=-1)(func)
    return click.argument("command")(func)


def hyper_quiet_opt(func):
    return click.option("-q", "--quiet", is_flag=True, help="Suppress logging")(func)


@group(
    name="hyper",
    short_help="Create hyperparameter searches",
    help="Create hyperparameter searches on Spell",
    docs="https://spell.ml/docs/hyper_searches/",
)
@click.pass_context
def hyper(ctx):
    pass


@hyper.command(
    name="list",
    short_help="List hyperparameter searches",
    docs="https://spell.ml/docs/hyper_searches/",
)
@click.pass_context
def list_hyper(ctx):
    """
    List all hyperparameter searches.
    """

    client = ctx.obj["client"]

    with api_client_exception_handler():
        searches = client.list_hyper_searches()

    data = []
    for hyper in searches:
        data.append((hyper.id, hyper.num_runs, prettify_time(hyper.created_at), hyper.creator.user_name))

    # the hyper list endpoint doesn't guarantee ordering
    data = sorted(data, key=lambda d: d[0])

    tabulate_rows(data, headers=["ID", "# RUNS", "CREATED AT", "CREATOR"])


@hyper.command(
    short_help="Describe a hyperparamater search",
    help="""Describe a hyperparamater search with the specified id""",
)
@click.pass_context
@click.argument("id")
def describe(ctx, id):
    def get_duration(obj):
        if obj.started_at is None:
            duration = "-"
        else:
            if obj.ended_at is None:
                end_time = datetime.now(tz=tzutc())
            else:
                end_time = obj.ended_at
            duration = prettify_timespan(obj.started_at, end_time)
        return duration

    client = ctx.obj["client"]

    with api_client_exception_handler():
        search = client.get_hyper_search(id)

    hyper_lines = [("ID", id)]

    # See also getTypeOfHyperSearch in SearchDetails.js in web.
    search_params_key = next(iter(search.parameter_spec.keys()))
    if search_params_key == "grid_params":
        search_type = "grid"
    elif search_params_key == "random_params":
        search_type = "random"
    elif search_params_key == "bayesian_params":
        search_type = "bayesian"
    else:
        raise ExitException("Found hyper search with unknown type {}.")
    hyper_lines.append(("Type", search_type))

    hyper_lines.append(("# Runs", len(search.runs)))
    hyper_lines.append(("Command", search.command))
    hyper_lines.append(("Machine Type", search.gpu))

    # See also getStatus in utils/hyperSearch.js in web.
    if search.ended_at is not None:
        status = "finished"
    elif search.started_at is None:
        status = "queued"
    else:
        status = "running"
    hyper_lines.append(("Status", status))

    hyper_lines.append(("Duration", get_duration(search)))
    hyper_lines.append(("Description", search.description if search.description != "" else "-"))

    click.echo("Hyperparameter Search Info:")
    tabulate_rows(hyper_lines)
    click.echo("\nRuns:")

    # a valid hyperparameter search always contains at least one run
    hyper_param_names = list(search.runs[0].hyper_params.keys())

    run_info_lines = []
    for run in search.runs:
        duration = get_duration(run)

        hyper_param_values = list(run.hyper_params.values())
        run_info_line = [run.id, run.status, duration]
        run_info_line.extend(hyper_param_values)
        run_info_lines.append(run_info_line)

    run_info_headers = ["Run ID", "Status", "Duration"]
    run_info_headers.extend(hyper_param_names)
    tabulate_rows(run_info_lines, headers=run_info_headers)


@hyper.command(
    name="grid",
    short_help="Execute a hyperparameter grid search",
    docs="https://spell.ml/docs/hyper_searches/#performing-grid-search",
)
@hyper_exec_args
@click.option(
    "--param",
    "params",
    multiple=True,
    metavar="NAME=VALUE[,VALUE,VALUE,...]",
    help="Specify a hyperparameter for the run. A run will be created for all "
    "hyperparameter value combinations provided. NAME should appear in the "
    'COMMAND surrounded by colons (i.e., ":NAME:" to indicate where '
    "the VALUE values should be substituted when creating each run.",
)
@json_hyper_param_option
@common_hyper_exec_options
@timeout_option
@stop_condition_option
@click.pass_context
def grid(
    ctx,
    command,
    args,
    params,
    json_params,
    provider,
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
    github_url,
    github_ref,
    stop_condition,
    tensorboard_dir,
    labels,
    timeout,
    project,
    **kwargs,
):
    """
    Execute a hyperparameter grid search for COMMAND remotely on Spell's infrastructure

    The grid command is used to create numerous runs simultaneously to perform a hyperparameter
    grid search. A run will be created for all possible combinations of parameters provided with
    the --param option.  All other options are the same as the spell run command and will apply
    to every run created in the hyperparameter search.
    """
    logger.info("starting hyper grid command")
    try:
        params = parse_list_params(params)
    except ParseException as e:
        raise ExitException(
            click.wrap_text(
                "Incorrect formatting of param '{}', it must be NAME=VALUE[,VALUE,VALUE,...]".format(e.token)
            ),
            SPELL_INVALID_CONFIG,
        )
    try:
        params.update(parse_list_params(json_params, is_json=True))
    except ParseException as e:
        raise ExitException(
            click.wrap_text("Incorrect formatting of json param '{}', it must be a json encoded list".format(e.token)),
            SPELL_INVALID_CONFIG,
        )
    try:
        stop_conditions = parse_conditions(stop_condition)
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
        "user",
        github_url,
        github_ref,
        timeout=timeout,
        stop_conditions=stop_conditions,
        tensorboard_dir=tensorboard_dir,
        labels=labels,
        **kwargs,
    )
    client = ctx.obj["client"]

    if project:
        run_req.project_id = get_or_create_project(client, project).id

    logger.info("sending hyper search request to api")
    with api_client_exception_handler():
        hyper = client.hyper_grid_search(params, run_req)
    utf8 = ctx.obj["utf8"]
    click.echo(with_emoji("💫", "Casting hyperparameter search #{}".format(hyper.id), utf8) + ellipses(utf8))

    # promote param names to attributes for tabulate
    for run in hyper.runs:
        run.id = str(run.id)
        for param in params:
            setattr(run, param, run.hyper_params[param])
    # display parameters and associated run IDs
    param_names = list(params.keys())
    headers = param_names + ["Run ID"]
    columns = list(params.keys()) + ["id"]
    tabulate_rows(hyper.runs, headers=headers, columns=columns)


@hyper.command(
    name="random",
    short_help="Execute a hyperparameter random search",
    docs="https://spell.ml/docs/hyper_searches/#performing-random-search",
)
@hyper_exec_args
@click.option(
    "-n",
    "--num-runs",
    "num_runs",
    required=True,
    type=int,
    prompt="Enter the total number of runs to execute",
    help="Total number of runs to create for the hyperparameter search",
)
@click.option(
    "-p",
    "--param",
    "params",
    multiple=True,
    metavar="NAME=VALUE[,VALUE,VALUE,...] | NAME=MIN:MAX[:linear|log|reverse_log[:int|float]]",
    help="Specify a hyperparameter for the run. Each run will sample this random parameter specification "
    "to determine a specific value for the run. The parameter values can be provided as either a "
    "list of values (from which one value will be randomly selected each run) or a range (MIN:MAX) "
    "and optional scaling ('linear', 'log', or 'reverse_log') and type ('int' or 'float'). "
    "If unspecified, a linear scaling and type float are assumed. NAME should appear in the "
    'COMMAND surrounded by colons (i.e., ":NAME:" to indicate where '
    "the VALUEs should be substituted when creating each run.",
)
@json_hyper_param_option
@common_hyper_exec_options
@timeout_option
@stop_condition_option
@click.pass_context
def random(
    ctx,
    command,
    args,
    num_runs,
    params,
    json_params,
    provider,
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
    github_url,
    github_ref,
    stop_condition,
    tensorboard_dir,
    labels,
    timeout,
    project,
    **kwargs,
):
    """
    Execute a hyperparameter random search for COMMAND remotely on Spell's infrastructure

    The random command is used to create numerous runs simultaneously to perform a hyperparameter
    search. As many runs as specified with --num-runs will be created and each hyperparameter specified with
    the --param option will be sampled to determine a specific value for each run.  All other options are the
    same as the spell run command and will apply to every run created in the hyperparameter search.
    """
    logger.info("starting hyper random command")
    try:
        params = parse_random_params(params)
    except ParseException as e:
        raise ExitException(
            click.wrap_text(
                "Incorrect formatting of param '{}', it must be NAME=VALUE[,VALUE,VALUE,...] or "
                "NAME=MIN:MAX[:linear|log|reverse_log[:int|float]]".format(e.token)
            ),
            SPELL_INVALID_CONFIG,
        )
    try:
        params.update(parse_list_params(json_params, is_json=True))
    except ParseException as e:
        raise ExitException(
            click.wrap_text("Incorrect formatting of json param '{}', it must be a json encoded list".format(e.token)),
            SPELL_INVALID_CONFIG,
        )
    try:
        stop_conditions = parse_conditions(stop_condition)
    except ParseException as e:
        raise ExitException(e.message)

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
        "user",
        github_url,
        github_ref,
        timeout=timeout,
        stop_conditions=stop_conditions,
        tensorboard_dir=tensorboard_dir,
        labels=labels,
        **kwargs,
    )
    client = ctx.obj["client"]

    if project:
        run_req.project_id = get_or_create_project(client, project).id

    logger.info("sending hyper search request to api")
    with api_client_exception_handler():
        hyper = client.hyper_random_search(params, num_runs, run_req)
    utf8 = ctx.obj["utf8"]
    click.echo(with_emoji("💫", "Casting hyperparameter search #{}".format(hyper.id), utf8) + ellipses(utf8))

    # promote param names to attributes for tabulate
    for run in hyper.runs:
        run.id = str(run.id)
        for param in params:
            setattr(run, param, run.hyper_params[param])
    # display parameters and associated run IDs
    param_names = list(params.keys())
    headers = param_names + ["Run ID"]
    columns = list(params.keys()) + ["id"]
    tabulate_rows(hyper.runs, headers=headers, columns=columns)


@hyper.command(
    name="bayesian",
    short_help="Execute a hyperparameter bayesian search",
    docs="https://spell.ml/docs/hyper_searches/#performing-bayesian-search",
)
@hyper_exec_args
@click.option(
    "-n",
    "--num-runs",
    "num_runs",
    required=True,
    type=int,
    prompt="Enter the maximum number of runs to execute",
    help="Maximum number of runs for the hyperparameter search",
)
@click.option(
    "-r",
    "--parallel-runs",
    "parallel_runs",
    required=True,
    type=int,
    prompt="Enter the number of runs to parallelize",
    help="Number of parallel runs to use for each iteration",
)
@click.option(
    "--metric",
    "metric",
    required=True,
    type=str,
    prompt="Enter the metric to optimize",
    help="Metric name that will be used ",
)
@click.option(
    "-a",
    "--metric-agg",
    "metric_agg",
    required=True,
    type=click.Choice(["avg", "min", "max", "last"]),
    prompt="Enter the metric aggregation method",
)
@click.option(
    "-p",
    "--param",
    "params",
    multiple=True,
    metavar="NAME=MIN:MAX[:int|float]",
    help="Specify a hyperparameter for the run in the form: a range (MIN:MAX) "
    "If unspecified, type float is assumed. NAME should appear in the "
    'COMMAND surrounded by colons (i.e., ":NAME:" to indicate where '
    "the VALUEs should be substituted when creating each run.",
)
@common_hyper_exec_options
@click.pass_context
def bayesian(
    ctx,
    command,
    args,
    num_runs,
    parallel_runs,
    metric,
    metric_agg,
    params,
    provider,
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
    github_url,
    github_ref,
    tensorboard_dir,
    labels,
    project,
    **kwargs,
):
    """
    Execute a hyperparameter bayesian search for COMMAND remotely on Spell's infrastructure

    The bayesian command is used to create parallelized bayesian optimization hyperparameter optimization
    with num_runs number of total runs, parallelized in sets of parallel_runs
    """
    logger.info("starting hyper bayesian command")
    try:
        params = parse_bayesian_params(params)

    except ParseException as e:
        raise ExitException(
            click.wrap_text("Incorrect formatting of param '{}', it must be NAME=MIN:MAX[:int|float]".format(e.token)),
            SPELL_INVALID_CONFIG,
        )

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
        "user",
        github_url,
        github_ref,
        tensorboard_dir=tensorboard_dir,
        labels=labels,
        **kwargs,
    )
    client = ctx.obj["client"]

    if project:
        run_req.project_id = get_or_create_project(client, project).id

    logger.info("sending hyper search request to api")
    with api_client_exception_handler():
        hyper = client.hyper_bayesian_search(params, num_runs, parallel_runs, metric, metric_agg, run_req)
    utf8 = ctx.obj["utf8"]
    click.echo(with_emoji("💫", "Casting hyperparameter search #{}".format(hyper.id), utf8) + ellipses(utf8))

    # promote param names to attributes for tabulate
    for run in hyper.runs:
        run.id = str(run.id)
        for param in params:
            setattr(run, param, run.hyper_params[param])
    # display parameters and associated run IDs
    param_names = list(params.keys())
    headers = param_names + ["Run ID"]
    columns = list(params.keys()) + ["id"]
    tabulate_rows(hyper.runs, headers=headers, columns=columns)


@hyper.command(
    name="stop",
    short_help="Stop a hyperparameter search",
    docs="https://spell.ml/docs/hyper_searches/#interrupting-a-hyperparameter-search",
)
@click.argument("hyper-search-id")
@hyper_quiet_opt
@click.pass_context
def stop(ctx, hyper_search_id, quiet):
    """
    Stop a hyperparameter search specified by HYPER-SEARCH-ID.

    All runs in the hyperparameter search that are running are sent a stop signal
    that ends current execution and transitions them to the "Saving" state.
    Stopped runs will continue to transition through the "Pushing" and "Saving" steps after stopping.
    If runs have not started yet, they are killed.  Any runs that are already in a final state are
    unaffected.
    """

    client = ctx.obj["client"]

    with api_client_exception_handler():
        logger.info("Stopping hyperparameter search {}".format(hyper_search_id))
        client.stop_hyper_search(hyper_search_id)

    if not quiet:
        click.echo("Stopping hyperparameter search {}.".format(hyper_search_id))


@hyper.command(
    name="kill",
    short_help="Kill a hyperparameter search",
    docs="https://spell.ml/docs/hyper_searches/#interrupting-a-hyperparameter-search",
)
@click.argument("hyper-search-id")
@hyper_quiet_opt
@click.pass_context
def kill(ctx, hyper_search_id, quiet):
    """
    Kill a hyperparameter search specified by HYPER-SEARCH-ID.

    All runs in the hyperparameter search are killed. Any runs that are already in a final state are
    unaffected.
    """

    client = ctx.obj["client"]

    with api_client_exception_handler():
        logger.info("Killing hyperparameter search {}".format(hyper_search_id))
        client.kill_hyper_search(hyper_search_id)

    if not quiet:
        click.echo("Killing hyperparameter search {}.".format(hyper_search_id))


@hyper.command(
    name="archive",
    short_help="Archive hyperparameter search",
    docs="https://spell.ml/docs/hyper_searches/",
)
@click.argument("hyper-search-id")
@click.pass_context
def archive_hyper(ctx, hyper_search_id):
    """
    Archive a hyperparameter search specified by HYPER-SEARCH-ID.
    """

    client = ctx.obj["client"]

    with api_client_exception_handler():
        client.archive_hyper_search(hyper_search_id)

    click.echo(hyper_search_id)


@hyper.command(
    name="download-metrics",
    short_help="Download metrics from a hyperparameter search",
    docs="https://spell.ml/docs/hyper_searches/",
)
@click.argument("hyper-search-id")
@download_metrics_params
@click.pass_context
def download_metrics_hyper(ctx, hyper_search_id, dest, force):
    """
    Download metrics from a hyperparameter search specified by HYPER-SEARCH-ID.
    """
    validate_download_dest(dest, force)
    client = ctx.obj["client"]

    metric_values = []
    with api_client_exception_handler():
        metric_names = client.list_hyper_metric_names(hyper_search_id)

    metric_names = [name["name"] for name in metric_names]

    for metric_name in metric_names:
        with api_client_exception_handler():
            runs_metrics = client.get_hyper_metric(hyper_search_id, metric_name)

        for run_id in runs_metrics:
            run_metrics = runs_metrics[run_id]["data"]
            metrics = [[int(run_id), metric_name] + values for values in run_metrics]
            metric_values += metrics

    write_rows(dest, metric_values, header=["run_id", "metric_name", "timestamp", "index", "value"])
    click.echo(f"Downloaded metrics to {dest}.")
