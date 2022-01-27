"""Build OCI images using docker buildx"""
from pathlib import Path
from sys import exit
from typing import List, Optional, Union

from kapla.cli.console import console, style_str
from kapla.cli.utils import map_string_to_dict
from kapla.docker.datatypes import BuildContext, Catalog, Image
from loguru import logger
from pydantic.error_wrappers import ValidationError
from python_on_whales import docker
from typer import Argument, Context, Option, Typer

app = Typer(
    name="builder",
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=False,
)


@app.command(
    "build", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def build(
    ctx: Context,
    name: Optional[str] = Argument(None, help="Name of images to build"),
    builder_file: Optional[str] = Option(
        None,
        "--builder-file",
        "-b",
        help="builder.yml file to use. By default files are searched accross repo",
    ),
    *,
    context: Optional[Path] = Option(
        None, "--context", "-c", help="Docker context to consider when performing build"
    ),
    file: Optional[Path] = Option(
        None,
        "--dockerfile",
        "--file",
        "-f",
        help="Custom Dockerfile to use when building image",
    ),
    tags: Optional[List[str]] = Option(
        None, "-t", "--tags", help="Custom tags to give to produced image"
    ),
    labels: Optional[List[str]] = Option(
        None, "-l", "--label", help="Additional labels to give to the produced image"
    ),
    platforms: Optional[List[str]] = Option(
        None, "-p", "--platform", help="Platforms to build the image for"
    ),
    add_hosts: Optional[List[str]] = Option(
        None,
        "-h",
        "--add-host",
        help="Add known hosts entries into the generated docker image",
    ),
    push: bool = Option(False, "--push", help="Push the image to registry after build"),
    load: bool = Option(
        False, "--load", help="Load the image into local docker engine after build"
    ),
    dump: bool = Option(
        False,
        "--dump",
        help="Dump the image filesystem into the current directory after build",
    ),
    build_args: Optional[List[str]] = Option(
        None, "--build-args", help="Additional build arguments"
    ),
    builder: Optional[str] = Option(
        None,
        "--builder",
        help="Custom builder to use (see --builder option for 'docker buildx build' command)",
    ),
    cache: bool = Option(
        True, "--cache", help="Cache generated layers to speed up build"
    ),
    cache_from: Optional[str] = Option(
        None,
        "--cache-from",
        help="Reuse cache from given location. Can be a remote docker image",
    ),
    cache_to: Optional[str] = Option(
        None,
        "--cache-to",
        help="Store intermediate layer and produced cache into given destination",
    ),
    network: Optional[str] = Option(
        None, "--network", help="Use a specific network mode during build"
    ),
    output: Optional[str] = Option(
        None, "--output", help="Custom output for 'docker buildx build' command"
    ),
    progress: str = Option("auto", "--progress", help="Progress display mode"),
    pull: bool = Option(False, "--pull", help="Always pull images before build"),
    secrets: Optional[List[str]] = Option(
        None, "--secret", help="Secrets to mount during build"
    ),
    # Don't know what those two options are for
    allow: Optional[List[str]] = None,
    ssh: Optional[str] = None,
    target: Optional[str] = None,
) -> None:
    """Build a docker image."""
    if builder_file:
        try:
            images = [Image.from_file(builder_file)]
        except ValidationError as err:
            console.print(err, style="red")
            exit(1)
    elif name:
        catalog = Catalog.from_directory(Path.cwd())
        try:
            images = [next(image for image in catalog.images if image.name == name)]
        except StopIteration:
            console.print(
                f"Build config for image {style_str(name, 'bold')} does not exist",
                style="red",
            )
            exit(1)
    else:
        try:
            images = Catalog.from_directory(Path.cwd()).images
        except ValidationError as err:
            console.print(err, style="red")
            exit(1)

    _add_hosts = map_string_to_dict(add_hosts)
    _labels = map_string_to_dict(labels or [])
    names = [tag for tag in tags] if tags else []

    is_key = True
    kwargs = {}
    for extra_arg in ctx.args:
        if is_key:
            key = extra_arg
            if key.startswith("--"):
                key = key[2:]
            elif key.startswith("-"):
                key = key[1:]
            if "=" in extra_arg:
                key, value = key.split("=")
                key = key.replace("-", "_").upper()
                kwargs[key] = value
                is_key = True
                continue
            else:
                is_key = False
                continue
        key = key.replace("-", "_").upper()
        kwargs[key] = extra_arg
        is_key = True
    _user_build_args = map_string_to_dict(build_args or [])
    _user_build_args = {**_user_build_args, **kwargs}

    if dump:
        _output = {"type": "local", "dest": "."}
    elif output:
        _output = map_string_to_dict(output)
    else:
        _output = {}

    if progress.lower() in ("0", "false", "no", "n"):
        _progress: Union[bool, str] = False
    else:
        _progress = progress

    # TODO: Is there some order ?
    for image in images:
        _build_args = {
            arg.name.upper(): arg.default
            for arg in image.build.build_args
            if arg.default
        }

        _build_args.update(
            {key.upper(): value for key, value in _user_build_args.items()}
        )
        _names = names or [image.get_name()]

        logger.debug(f"Building image {_names[0]} with build arguments: {_build_args}")
        if len(_names) > 1:
            for name in _names[1:]:
                logger.debug(f"Using additional tag: {name}")

        build_context = BuildContext(
            context_path=context or image.build.context,
            add_hosts=_add_hosts or image.build.add_hosts,
            allow=list(allow or []),
            build_args=_build_args,
            builder=builder,
            cache=cache,
            cache_from=cache_from,
            cache_to=cache_to,
            file=file or image.build.file,
            labels={**image.labels, **_labels},
            load=load,
            network=network,
            output=_output,
            platforms=list(platforms or []) or image.platforms,
            progress=_progress,
            pull=pull,
            push=push,
            secrets=secrets,
            ssh=ssh,
            tags=_names,
            target=target,
        )
        docker.buildx.build(**build_context.dict())
