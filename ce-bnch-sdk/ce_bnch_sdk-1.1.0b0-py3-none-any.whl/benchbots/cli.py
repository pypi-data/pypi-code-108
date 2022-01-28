import os
import pathlib
import shutil
from typing import cast

import typer
import yaml

from benchling_sdk.auth.api_key_auth import ApiKeyAuth
from benchling_sdk.benchbots.benchling_store import BenchlingStore
from benchling_sdk.benchbots.codegen.generate_dependencies_module import generate_dependencies_module
from benchling_sdk.benchbots.codegen.generate_models import generate_models
from benchling_sdk.benchbots.commands.validate_manifest import validate_manifest_yaml
from benchling_sdk.benchbots.dependencies.benchling_dependency_resolver import BenchlingDependencyResolver
from benchling_sdk.benchbots.dependencies.dependency_linker import DependencyLinker
from benchling_sdk.benchbots.helpers.tokens import api_key_from_prompt_or_keyring
from benchling_sdk.benchbots.types.dependency_links import DependencyLinks
from benchling_sdk.benchbots.types.manifest import Manifest
from benchling_sdk.benchling import Benchling

benchbots_cli = typer.Typer()

manifest_cli = typer.Typer()
benchbots_cli.add_typer(
    manifest_cli, name="manifest", help="The manifest file declares the Benchbot's identity and requirements."
)

DEFAULT_MANIFEST_FILE_PATH = "manifest.yaml"
DEFAULT_DEPENDENCIES_FILE_PATH = "modules/modules/dependencies.py"
DEFAULT_MODEL_DIRECTORY_PATH = "modules/modules/generated_models"
MANIFEST_OPTION = typer.Option(DEFAULT_MANIFEST_FILE_PATH, "--manifest-file-path", "-m")


@manifest_cli.command(name="validate")
def validate(manifest_file_path: str = MANIFEST_OPTION):
    """Validate your Benchbot manifest's file format."""
    with open(manifest_file_path) as f:
        validate_manifest_yaml(f.read())
    typer.secho(f"Success! No issues found in {manifest_file_path}.", fg="green")


@manifest_cli.command(name="get")
def get_manifest(
    id: str,
    hostname: str,
    manifest_file_path: str = MANIFEST_OPTION,
    overwrite: bool = False,
    reset_api_key: bool = False,
):
    """Get a Benchbot's manifest and write it to a local file."""
    manifest_path = pathlib.Path(manifest_file_path)
    if not overwrite and manifest_path.exists():
        typer.secho(
            f"Manifest file {manifest_file_path} already exists. To overwrite, use the option --overwrite.",
            fg="red",
        )
        raise typer.Exit(code=1)

    api_key = api_key_from_prompt_or_keyring(hostname, reset_api_key)
    client = Benchling(hostname, auth_method=ApiKeyAuth(api_key))
    url = f"v2-alpha/apps/{id}/manifest.yaml"

    response = client.api.get(url)
    typer.secho(response.text)
    with open(manifest_file_path, "w+") as manifest_file:
        manifest_file.write(cast(str, response.text))

    typer.secho(f"Successfully wrote manifest for Benchbot {id} to {manifest_file_path}.", fg="green")


@benchbots_cli.command(name="install")
def install_manifest(hostname: str, manifest_file_path: str = MANIFEST_OPTION, reset_api_key: bool = False):
    """Install or update a Benchbot from a manifest file."""
    manifest_path = pathlib.Path(manifest_file_path)
    if not manifest_path.exists():
        typer.secho(f"Manifest file path {manifest_file_path} does not exist.", fg="red")
        raise typer.Exit(code=1)

    api_key = api_key_from_prompt_or_keyring(hostname, reset_api_key)
    client = Benchling(hostname, auth_method=ApiKeyAuth(api_key))

    with open(manifest_file_path) as manifest_file:
        manifest_text = manifest_file.read()

        # TODO validate manifest once we include all required fields in the yaml definition (e.g. version).
        # validate_manifest_yaml(manifest)

        manifest_dict = yaml.load(manifest_text, Loader=yaml.SafeLoader)
        id_ = manifest_dict.get("info", {}).get("id")
        url = f"v2-alpha/apps/{id_}/manifest.yaml"
        client.api.put(url, content=manifest_text, additional_headers={"Content-Type": "text/yaml"})
        typer.secho(f"Successfully installed Benchbot {id_} from {manifest_file_path}.", fg="green")


dependencies_cli = typer.Typer()
benchbots_cli.add_typer(
    dependencies_cli,
    name="dependencies",
    help="Dependencies allow a Benchbot to depend on resources within a tenant in a portable way, without hard-coding the API IDs.",
)


@dependencies_cli.command(name="scaffold")
def scaffold(
    manifest_file_path: str = MANIFEST_OPTION,
    dependencies_file_path: str = DEFAULT_DEPENDENCIES_FILE_PATH,
    model_directory_path: str = DEFAULT_MODEL_DIRECTORY_PATH,
):
    """Auto-generate Python code for accessing your Benchbot's dependencies at run-time."""
    manifest = Manifest.from_file(manifest_file_path)
    if not manifest.dependencies:
        typer.echo("Skipping code generation because the manifest has no dependencies.")
        return

    if os.path.exists(dependencies_file_path):
        typer.echo(f"Overwriting existing dependency file {dependencies_file_path}")
    else:
        typer.echo(f"Creating new dependency file {dependencies_file_path}")

    with open(dependencies_file_path, "w") as f:
        f.write(generate_dependencies_module(manifest))

    typer.secho(
        f"Success! Generated dependency file for {manifest.info.name} {manifest.info.version} "
        f"at {dependencies_file_path}.",
        fg="green",
    )

    if os.path.exists(model_directory_path):
        shutil.rmtree(model_directory_path)
        typer.echo(f"Removing existing directory {model_directory_path}")

    typer.echo(f"Creating model files in new directory {model_directory_path}")
    os.mkdir(model_directory_path)
    with open(os.path.join(model_directory_path, "__init__.py"), "w") as f:
        f.write("")

    for model_name, model_file in generate_models(manifest).items():
        file_path = os.path.join(model_directory_path, f"{model_name}.py")
        with open(file_path, "w") as f:
            f.write(model_file)
            typer.secho(
                f"Success! Generated model file {file_path}",
                fg="green",
            )


@dependencies_cli.command(name="link")
def link(
    dependency_links_file_path: str,
    hostname: str,
    manifest_file_path: str = MANIFEST_OPTION,
    reset_api_key: bool = False,
) -> None:
    """Link your Benchbot's dependencies to resources in your tenant."""
    api_key = api_key_from_prompt_or_keyring(hostname, reset_api_key)
    benchling_store = BenchlingStore(Benchling(hostname, auth_method=ApiKeyAuth(api_key)))
    dependency_resolver = BenchlingDependencyResolver(benchling_store)
    dependency_linker = DependencyLinker(dependency_resolver)
    manifest = Manifest.from_file(manifest_file_path)

    dependency_links = None
    if os.path.exists(dependency_links_file_path):
        typer.echo("Existing dependency link file found")
        dependency_links = DependencyLinks.from_file(dependency_links_file_path)
    else:
        typer.echo("No existing dependency link file found, creating a new one")

    dependency_links = dependency_linker.link_dependencies(dependency_links, manifest)

    with open(dependency_links_file_path, "w") as f:
        f.write(dependency_links.to_json(indent=2))

    typer.echo(
        typer.style(f"Success! Dependency link file updated: {dependency_links_file_path}.", fg="green")
    )
