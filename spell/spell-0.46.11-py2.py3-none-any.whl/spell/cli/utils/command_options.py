from functools import wraps

import click

from spell.cli.api_constants import (
    get_machine_types,
    get_machine_type_default,
)
from spell.cli.exceptions import ExitException, SPELL_INVALID_CONFIG
from spell.cli.utils import LazyChoice
from spell.shared.dependencies import (
    NoEnvFound,
    InvalidDependencyConfig,
)
from spell.cli.utils.dependencies import (
    dependencies_from_env,
)


def deps_from_env_callback(ctx, param, value):
    if not value:
        return None
    try:
        return dependencies_from_env()
    except (InvalidDependencyConfig, NoEnvFound) as e:
        raise ExitException(e.message, SPELL_INVALID_CONFIG)


def dependency_params(include_docker=True, resource_type="run"):
    """Creates a decorator for adding run dependency CLI options"""

    def dependency_params_inner(f):
        """Adds run dependency CLI options"""

        @click.option(
            "--deps-from-env",
            "python_env_deps",
            help="Determine Python dependencies from the current Conda or Pip environment",
            is_flag=True,
            default=False,
            callback=deps_from_env_callback,
        )
        @click.option(
            "--pip-req",
            "requirements_file",
            help="Requirements file to install using pip",
            type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True),
            default=None,
        )
        @click.option("--pip", "pip_packages", help="Single dependency to install using pip", multiple=True)
        @click.option(
            "--conda-file",
            help="Path to conda specification file or YAML environment file",
            type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True),
            default=None,
        )
        @click.option("--apt", "apt_packages", help="Dependency to install using apt", multiple=True)
        @click.option(
            "-e",
            "--env",
            "envvars",
            multiple=True,
            help="Add an environment variable to the {}".format(resource_type),
        )
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        if include_docker:
            wrapper = (
                click.option(
                    "--docker-image",
                    "--docker_image",
                    "--from",
                    "docker_image",
                    help="Custom docker image to run from. "
                    "Specify image as <domain>/<repository>/<image_name>:<tag>. "
                    "Default to docker.io if <domain>/ is omitted."
                    "To use images from a private container registry "
                    "first run 'spell cluster add-docker-registry'.",
                )
            )(wrapper)

        return wrapper

    return dependency_params_inner


def workspace_spec_params(f):
    """Adds run workspace specification CLI options"""

    @click.option("-c", "--commit-ref", default="HEAD", help="Git commit hash to use")
    @click.option("--github-url", help="GitHub URL of a repository to use")
    @click.option(
        "--github-ref",
        help="commit hash, branch, or tag of the repository to pull (default: 'master')",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def machine_config_params(exclude_kubernetes=False):
    """Adds run machine configuration CLI options"""

    def machine_config_params_inner(f):
        @click.option(
            "-t",
            "--machine-type",
            type=LazyChoice(get_machine_types),
            help="Machine type to run on",
        )
        @mount_params
        @click.option(
            "--local-caching",
            hidden=True,
            is_flag=True,
            help="enable local caching of attached resources",
        )
        @click.option(
            "--provider",
            hidden=True,
            help="if specified only machines from that provider will be used" " e.g. aws",
        )
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Validate user isn't using `--machine-type` on a k8s run
            if kwargs.get("machine_type") and kwargs.get("node_group"):
                raise ExitException(
                    "--machine-type and --node-group options are mutually exclusive", SPELL_INVALID_CONFIG
                )
            if kwargs.get("machine_type") and kwargs.get("kubernetes"):
                raise ExitException(
                    "--machine-type is not used by Kubernetes runs, use --node-group instead", SPELL_INVALID_CONFIG
                )

            # Set defaults for regular/k8s runs
            if kwargs.get("kubernetes") and not kwargs.get("node_group"):
                kwargs["node_group"] = "default"
            elif not kwargs.get("machine_type"):
                kwargs["machine_type"] = get_machine_type_default()

            return f(*args, **kwargs)

        if not exclude_kubernetes:
            wrapper = (
                click.option(
                    "--kubernetes",
                    is_flag=True,
                    hidden=True,
                    help="Execute on a Kubernetes cluster using default node-group",
                )
            )(wrapper)
            wrapper = (
                click.option(
                    "--node-group",
                    hidden=True,
                    help="Node group to schedule the run to (K8s-only). Cannot be "
                    "used in conjunction with --machine-type.",
                )
            )(wrapper)

        return wrapper

    return machine_config_params_inner


def cli_params(f):
    """Adds miscellanous CLI options"""

    @click.option("-f", "--force", is_flag=True, help="Skip interactive prompts")
    @click.option("-v", "--verbose", is_flag=True, help="Print additional information")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def description_param(resource_type="run"):
    def wrapper(f):
        """Adds run description CLI option"""

        @click.option(
            "-d",
            "--description",
            default=None,
            help="Description of the {}. If unspecified defaults to the current commit message".format(resource_type),
        )
        @wraps(f)
        def wrapper_inner(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper_inner

    return wrapper


def label_param(f):
    """Adds label CLI option"""

    @click.option(
        "--label",
        "labels",
        multiple=True,
        help="Label to add to the run. Can specify more than one.",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


RESOURCE_SPECIFICATION_HELP = (
    "The resource (specified by a Spell resource path) is required. "
    "An optional mount path within the container can also be specified, separated by a "
    "colon from the resource name. If the mount path is omitted, it defaults to the base name "
    "of the resource (e.g., 'mnist' for 'public/image/mnist'). "
    "Example: --mount runs/42:/mnt/data"
)


def mount_params(f):
    @click.option(
        "-m",
        "--mount",
        "raw_resources",
        multiple=True,
        metavar="RESOURCE[:MOUNT_PATH]",
        help="Attach a resource file or directory (e.g., from a run output, public dataset, "
        f"or upload). {RESOURCE_SPECIFICATION_HELP}",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def background_option(f):
    """Adds background CLI option"""

    @click.option("-b", "--background", is_flag=True, help="Do not print logs")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def idempotent_option(f):
    """Adds idempotent run option"""

    @click.option(
        "--idempotent",
        hidden=True,
        is_flag=True,
        help="Use an existing identical run if one is found instead of launching a new one",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def project_option(f):
    """Adds 'project' run option"""

    @click.option(
        "--project",
        "-p",
        help="Name of project to add this run to",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def timeout_option(f):
    """Adds timeout run option"""

    @click.option(
        "--timeout",
        type=int,
        help="If the run is still running after this many minutes we will stop the run and save any outputs",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def tensorboard_params(f):
    """Adds run tensorboard specification CLI options"""

    @click.option(
        "--tensorboard-dir",
        help="The path where tensorboard files will be read from",
        type=click.Path(exists=False, dir_okay=True, writable=True, readable=True),
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def stop_condition_option(f):
    """Adds --stop-condition run option"""

    @click.option(
        "--stop-condition",
        multiple=True,
        metavar="METRIC_NAME OPERATOR VALUE[:MIN_INDEX]",
        help="METRIC_NAME is the name of a metric the run produces. OPERATOR is <, >, <=, or >=. "
        "VALUE is a float. During the run if there is a metric value that meets the condition the "
        "run will be stopped. You can optionally provide a MIN_INDEX integer. In that case, only values "
        "of the metric starting with that index will be considered.",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def json_hyper_param_option(f):
    """Adds --json-param hyper search option"""

    @click.option(
        "--json-param",
        "json_params",
        multiple=True,
        metavar="NAME='[VALUE,VALUE,...]'",
        help="Specify a hyperparameter for the run. This should be formatted as a JSON array. "
        "This can be used instead of --param if you want a list of values which contain commas. "
        "A run will be created for all hyperparameter value combinations "
        "provided. NAME should appear in the COMMAND surrounded by colons "
        '(i.e., ":NAME:" to indicate where the VALUE values should be substituted '
        "when creating each run.",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def download_metrics_params(f):
    """Adds --dest and --force options."""

    @click.option(
        "-d",
        "--dest",
        type=click.Path(file_okay=True, dir_okay=False, writable=True, readable=True),
        default="metrics.csv",
        help="Destination file path. Defaults to metrics.csv",
    )
    @click.option("-f", "--force", is_flag=True, help="Overwrite existing file")
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper
