import click

from tktl.cli.common import (
    ClickGroup,
    get_secrets,
    validate_integration_shared_options,
    validate_project_shared_options,
)
from tktl.commands.validate import (
    build_image,
    get_docker_manager,
    validate_endpoint_sample,
    validate_import,
    validate_integration,
    validate_profiling,
    validate_project_config,
    validate_unittest,
)
from tktl.core.config import settings


@click.group(
    "validate", help="Validate the project", cls=ClickGroup, **settings.HELP_COLORS_DICT
)
def validate():
    pass


@validate.command("config", help="Validate the configuration")
@click.option(
    "--path", "-p", help="Validate project located at this path", type=str, default="."
)
def validate_config_command(path) -> None:
    """Validates a new project for the necessary scaffolding, as well as the supporting
    files needed. The directory structure of a new project.
    """
    validate_project_config(path=path)


@validate.command("import", help="Validate src/endpoints.py")
@validate_project_shared_options
@click.option(
    "--secrets-repository",
    "-s",
    help="Full repository name (owner/name) to use from which to get the secret names",
    required=False,
)
def validate_import_command(
    path: str, cache: bool, prune: bool, secrets_repository: str
) -> None:
    secrets = get_secrets(secrets_repository)
    dm = get_docker_manager(path=path)
    image = build_image(dm=dm, path=path, cache=cache, prune=prune, secrets=secrets)
    validate_import(dm=dm, image=image)
    if prune:
        dm.remove_image(image)


@validate.command("sample", help="Validate Sample Data on Endpoints")
@validate_project_shared_options
@click.option(
    "--secrets-repository",
    "-s",
    help="Full repository name (owner/name) to use from which to get the secret names",
    required=False,
)
def validate_sample_command(
    path: str, cache: bool, prune: bool, secrets_repository: str
) -> None:
    secrets = get_secrets(secrets_repository)
    dm = get_docker_manager(path=path)
    image = build_image(dm=dm, path=path, cache=cache, prune=prune, secrets=secrets)
    validate_endpoint_sample(dm=dm, image=image)
    if prune:
        dm.remove_image(image)


@validate.command("unittest", help="Validate the unittests")
@validate_project_shared_options
@click.option(
    "--secrets-repository",
    "-s",
    help="Full repository name (owner/name) to use from which to get the secret names",
    required=False,
)
def validate_unittest_command(
    path: str, cache: bool, prune: bool, secrets_repository: str
) -> None:
    secrets = get_secrets(secrets_repository)
    dm = get_docker_manager(path=path)
    image = build_image(dm=dm, path=path, cache=cache, prune=prune, secrets=secrets)
    validate_unittest(dm=dm, image=image)
    if prune:
        dm.remove_image(image)


@validate.command("integration", help="Validate integration")
@validate_integration_shared_options
@validate_project_shared_options
@click.option(
    "--secrets-repository",
    "-s",
    help="Full repository name (owner/name) to use from which to get the secret names",
    required=False,
)
def validate_integration_command(
    path: str,
    cache: bool,
    prune: bool,
    timeout: int,
    retries: int,
    secrets_repository: str,
) -> None:
    secrets = get_secrets(secrets_repository)
    dm = get_docker_manager(path=path)
    image = build_image(dm=dm, path=path, cache=cache, prune=prune, secrets=secrets)
    validate_integration(dm=dm, image=image, timeout=timeout, retries=retries)
    if prune:
        dm.remove_image(image)


@validate.command("profiling", help="Validate profiling")
@validate_integration_shared_options
@validate_project_shared_options
@click.option(
    "--secrets-repository",
    "-s",
    help="Full repository name (owner/name) to use from which to get the secret names",
    required=False,
)
def validate_profiling_command(
    path: str,
    cache: bool,
    prune: bool,
    timeout: int,
    retries: int,
    secrets_repository: str,
) -> None:
    secrets = get_secrets(secrets_repository)
    dm = get_docker_manager(path=path)
    image = build_image(dm=dm, path=path, cache=cache, prune=prune, secrets=secrets)
    validate_profiling(
        dm=dm, image=image, timeout=timeout, retries=retries, prune=prune
    )
    if prune:
        dm.remove_image(image)


@validate.command("all", help="Validate everything")
@validate_integration_shared_options
@validate_project_shared_options
@click.option(
    "--secrets-repository",
    "-s",
    help="Full repository name (owner/name) to use from which to get the secret names",
    required=False,
)
def validate_all_command(
    path: str,
    cache: bool,
    prune: bool,
    timeout: int,
    retries: int,
    secrets_repository: str,
) -> None:
    validate_project_config(path=path)

    secrets = get_secrets(secrets_repository)
    dm = get_docker_manager(path=path)
    image = build_image(dm=dm, path=path, cache=cache, prune=prune, secrets=secrets)

    validate_import(dm=dm, image=image)
    validate_endpoint_sample(dm=dm, image=image)
    validate_unittest(dm=dm, image=image)
    validate_integration(dm=dm, image=image, timeout=timeout, retries=retries)
    validate_profiling(
        dm=dm, image=image, timeout=timeout, retries=retries, prune=prune
    )

    if prune:
        dm.remove_image(image)
