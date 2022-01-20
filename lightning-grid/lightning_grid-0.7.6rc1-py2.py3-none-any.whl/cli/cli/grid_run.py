from collections import OrderedDict
from pathlib import Path
import shlex
import sys
from typing import Dict, Optional

import click
import yaspin

from grid import Run, Resources, ScratchSpace
from grid.cli import rich_click
from grid.cli.cli.utilities import verify_entrypoint_script
from grid.cli.utilities import check_description_isnt_too_long
import grid.sdk.env as env
from grid.sdk.rest.exceptions import GridException
from grid.sdk.datastores import fetch_datastore
from grid.sdk.utils.name_generator import unique_name


def _check_run_name_is_valid(_ctx, _param, value):
    """Click callback that checks if a Run contains reserved names."""
    if value is not None:
        fail = False

        #  Check if the input is alphanumeric.
        _run_name = value.replace('-', '')
        if not _run_name.isalnum():
            fail = True

        #  Check if the allowed `-` character is not used
        #  at the end of the string.
        elif value.endswith('-') or value.startswith('-'):
            fail = True

        #  Check that the run name does not contain any
        #  uppercase characters.
        elif any(x.isupper() for x in value):
            fail = True

        if fail:
            raise click.BadParameter(
                f"""

            Invalid Run name: {value} the Run name must be lower case
            alphanumeric characters or '-', start with an alphabetic
            character, and end with an alphanumeric character (e.g. 'my-name',
            or 'abc-123').

                """
            )

    return value


def _check_ignore_warnings_flag(ctx, _param, value):
    """
    Click callback that assigns the value of the ignore warnings callback
    to a global variable.
    """
    if value is not None:
        env.IGNORE_WARNINGS = value
    return value


def _aws_node_to_nickname():
    aws_node_to_nicknames = OrderedDict({
        # AWS
        'p3.16xlarge': '8_v100_16gb',
        'p3dn.24xlarge': '8_v100_32gb',
        'g4dn.metal': '8_t4_16gb',
        'p2.8xlarge': '8_k80_12gb',
        'p3.8xlarge': '4_v100_16gb',
        'g4dn.12xlarge': '4_t4_16gb',
        'g3.16xlarge': '4_m60_8gb',
        'g3.8xlarge': '2_m60_8gb',
        'p3.2xlarge': '1_v100_16gb',
        # 'p4d.24xlarge': '8_a100_40gb',  # currently not supported
        'g4dn.8xlarge': '1_t4_16gb',
        'g4dn.4xlarge': '1_t4_16gb',
        'g4dn.2xlarge': '1_t4_16gb',
        'g4dn.xlarge': '1_t4_16gb',
        'g4dn.16xlarge': '1_t4_16gb',
        'p2.xlarge': '1_k80_12gb',
        'g3s.xlarge': '1_m60_8gb',
        'g3.4xlarge': '1_m60_8gb',
        't2.large': '2_cpu_8gb',
        't2.medium': '2_cpu_4gb'
    })
    return aws_node_to_nicknames


def _nickname_to_aws_nodes():
    aws_node_to_nickname = _aws_node_to_nickname()
    aws_nickname_to_node = {v: k for k, v in aws_node_to_nickname.items()}
    return aws_nickname_to_node


def _resolve_instance_type_nickname(ctx, _param, value):
    """
    Enables instance type shortcuts like:
    2_cpu_4gb for t2.large
    """
    nickname = value.lower()

    aws_nickname_to_node = _nickname_to_aws_nodes()

    # validate potential options for the node name
    possible_values = list(aws_nickname_to_node.keys()) + list(aws_nickname_to_node.values())
    if nickname not in possible_values:
        possible_options = '\n'.join(list(aws_nickname_to_node.keys()))
        click.BadParameter(f'{nickname} is not an available instance_type\n try one of these:\n{possible_options}')

    instance_type = nickname

    # if the value has _ then it's a nickname
    if '_' in nickname:
        instance_type = aws_nickname_to_node[nickname]
    return instance_type


def _get_instance_types(ctx, args, incomplete):
    # TODO: these should be retrieved from backend
    return list(_aws_node_to_nickname().keys())


def _run_command_builder(ctx, _param, value):
    # Captures invocation command exactly as it was
    # typed in the terminal. pipe.quote maintains original
    # quotation used in the CLI. We'll replace absolute
    # grid executable path with the `grid` alias.
    script = value[0]
    verify_entrypoint_script(script)
    sys.argv[0] = "grid"
    invocation_command = " ".join(map(shlex.quote, sys.argv))
    _, script_args = invocation_command.split(script)
    return f"{script} {script_args}"


@rich_click.command(context_settings=dict(ignore_unknown_options=True))
@click.option('--config', 'config', type=Path, required=False, help='Path to Grid config YML.')
@click.option('--name', 'name', type=str, required=False, help='Name for this run', callback=_check_run_name_is_valid)
@click.option(
    '--description',
    'description',
    type=str,
    required=False,
    help='Run description; useful for note-keeping',
    callback=check_description_isnt_too_long
)
@click.option('--cluster', 'cluster', type=str, default=env.CONTEXT, required=False)
@click.option(
    '--strategy',
    'strategy',
    type=click.Choice(['grid_search', 'random_search'], case_sensitive=False),
    required=False,
    help='Hyper-parameter search strategy'
)
@click.option('--trials', 'trials', type=int, required=False, help='Number of trials to run hyper parameter search')
@click.option(
    '--instance_type',
    'instance_type',
    type=str,
    default='t2.medium',
    help='Instance type to start training session in',
    autocompletion=_get_instance_types,
    callback=_resolve_instance_type_nickname
)
@click.option('--gpus', 'gpus', type=int, required=False, default=0, help='Number of GPUs to allocate per experiment')
@click.option('--cpus', 'cpus', type=int, required=False, default=1, help='Number of CPUs to allocate per experiment')
@click.option('--memory', 'memory', type=str, default="100", required=False, help='How much memory an experiment needs')
@click.option(
    '--datastore_name', 'datastore_name', type=str, required=False, help='Datastore name to be mounted in training'
)
@click.option(
    '--datastore_version',
    'datastore_version',
    type=int,
    required=False,
    help='Datastore version to be mounted in training'
)
@click.option(
    '--datastore_mount_dir',
    'datastore_mount_dir',
    type=str,
    required=False,
    help='Directory to mount Datastore in training job'
)
@click.option(
    '--framework',
    'framework',
    type=click.Choice(['lightning', 'torch', 'tensorflow', 'julia', 'torchelastic'], case_sensitive=False),
    required=False,
    default='lightning',
    help='Framework to use in training'
)
@click.option(
    '--use_spot',
    'use_spot',
    is_flag=True,
    required=False,
    help='Use spot instance. The spot instances, or preemptive instance can be shut down at will'
)
@click.option(
    '--ignore_warnings',
    is_flag=True,
    required=False,
    help='If we should ignore warning when executing commands',
    callback=_check_ignore_warnings_flag
)
@click.option(
    '--scratch_size',
    type=int,
    default=100,
    required=False,
    help='The size in GB of the scratch space attached to the experiment'
)
@click.option(
    '--scratch_mount_path',
    type=str,
    required=False,
    help='The mount path to mount the scratch space',
    default='/tmp/scratch',
)
@click.option(
    '-l',
    '--localdir',
    is_flag=True,
    required=False,
)
@click.option('-d', '--dockerfile', type=str, required=False, help="Dockerfile for the image building")
@click.option(
    '--dependency_file',
    type=str,
    required=False,
    help="Dependency file path. If not provided and if either "
    "`requirements.txt` or `environment.yml` is present "
    "in the current-working-directory, that'll be used"
)
@click.option(
    '--auto_resume',
    'auto_resume',
    is_flag=True,
    required=False,
    help="Mark this run as auto-resumable. "
    "If underlying node/instance/VM is terminated experiment will be automatically resumed, with all "
    "artifacts restores from the last known state. The experiment code will receive SIGTERM signal"
    "and it must exit with status code 0 upon properly dumping its state to disk"
)
@rich_click.argument(
    'run_command', nargs=-1, callback=_run_command_builder, help='Arguments to be passed to the script.'
)
def run(
    run_command: str,
    config: Optional[Dict],
    name: Optional[str],
    cluster: Optional[str],
    strategy: Optional[str],
    trials: Optional[int],
    instance_type: str,
    gpus: Optional[int],
    description: Optional[str],
    ignore_warnings: bool,
    memory: Optional[str],
    cpus: Optional[int],
    datastore_name: Optional[str],
    datastore_version: Optional[int],
    datastore_mount_dir: Optional[str],
    framework: Optional[str],
    use_spot: Optional[bool],
    scratch_size: Optional[int],
    scratch_mount_path: Optional[str],
    localdir: Optional[bool],
    dockerfile: Optional[str],
    dependency_file: Optional[str],
    auto_resume: Optional[bool] = None,
) -> None:
    """Launch a Run from some SCRIPT with the provided SCRIPT_ARGS.

    A run is a collection of experiments which run with a single set of SCRIPT_ARGS. The
    SCRIPT_ARGS passed to the run command can represent fixed values, or a set of values
    to be searched over for each option. If a set of values are passed, a sweep (grid-search
    or random-search) will be performed, launching the desired number of experiments in
    parallel - each with a unique set of input arguments.

    The script runs on the specified instance type and Grid collects the generated
    artifacts, metrics, and logs; making them available for you to view in real time
    (or later if so desired) on either our Web UI or via this CLI.
    """

    # Setting this to the global variable so downstream tasks can pick it up easily
    if ignore_warnings:
        env.IGNORE_WARNINGS = ignore_warnings

    if env.DEBUG:
        click.echo(f"Run command: {run_command}")
        click.echo(f"Hyperparams Search Strategy: {strategy}")
        click.echo(f"GPUs Requested: {gpus}")
        click.echo(f"Spot Requested: {use_spot}")

    # make a fun random name when user does not pass in a name
    if name is None:
        name = unique_name()

    dstore = None
    if datastore_name:
        dstore = fetch_datastore(datastore_name, datastore_version, cluster)

    # these values will be overwritten by values in the config file if they exist
    resources = Resources(instance_type=instance_type, gpus=gpus, cpus=cpus, storage_gb=int(memory), use_spot=use_spot)
    scratch = ScratchSpace(size_gb=scratch_size, mount_path=scratch_mount_path)

    # starting the spinner
    spinner = yaspin.yaspin(text=f"Submitting Run {name} ...", color="yellow")
    spinner.start()
    try:
        run_obj = Run(
            name=name,
            run_command=run_command,
            description=description,
            strategy=strategy,
            num_trials=trials,
            framework=framework,
            dependency_file=dependency_file,
            localdir=localdir,
            dockerfile=dockerfile,
            auto_resume=auto_resume,
            resources=resources,
            datastore=dstore,
            datastore_mount_dir=datastore_mount_dir,
            scratch=scratch,
            cluster_id=cluster,
            config_file=config,
        )

        # when starting a localdir run, the local directory is uploaded to s3.
        # The upload bar and the spinner interfere, causing lots of noise
        if localdir:
            spinner.stop()

        run_obj.start()
    except GridException as e:
        spinner.fail("✘")
        raise click.ClickException(str(e))
    finally:
        # stopping the spinner
        spinner.stop()

    if run_obj.exists:
        datastore_name = run_obj.datastore.name if run_obj.datastore else "None"
        datastore_version = run_obj.datastore.version if run_obj.datastore else "None"
        datastore_mount_dir = run_obj.datastore_mount_dir if run_obj.datastore_mount_dir else "None"
        message = f"""
                    Run submitted!
                    `grid status` to list all runs
                    `grid status {run_obj.name}` to see all experiments for this run

                    ----------------------
                    Submission summary
                    ----------------------
                    name:                    {run_obj.name}
                    run_command:             {run_obj.run_command}
                    instance_type:           {run_obj.resources.instance_type}
                    use_spot:                {run_obj.resources.use_spot}
                    cluster:                 {run_obj.cluster_id}
                    datastore_name:          {datastore_name}
                    datastore_version:       {datastore_version}
                    datastore_mount_dir:     {datastore_mount_dir}
                    """
        click.echo(message)
    else:
        click.echo(f"Run {name} failed to submit")
