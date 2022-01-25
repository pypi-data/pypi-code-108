import platform
import json
import multiprocessing
import yamale
import yaml
from pathlib import Path
from typing import Iterable, Union
import docker

MAX_NUM_WORKERS = int(multiprocessing.cpu_count() // 2)
WORKFLOW_SCHEMA_PATH = Path(__file__).parent / "workflow-schema.yaml"


def _absolute_path(path: Union[Path, str] = None) -> Path:
    _path = (
        Path.cwd() if path is None else path if isinstance(path, Path) else Path(path)
    ).resolve()
    if not _path.exists():
        raise FileNotFoundError(f"Cannot locate path: {_path}")
    return _path


def _absolute_file(path: Union[Path, str] = None) -> Path:
    _path = _absolute_path(path)
    if not _path.is_file():
        raise FileNotFoundError(f"{_path} is not a file!")
    return _path


def _absolute_dir(path: Union[Path, str] = None) -> Path:
    _path = _absolute_path(path)
    if not _path.is_dir():
        raise FileNotFoundError(f"{_path} is not a directory!")
    return _path


def get_high_level_docker_api():
    return docker.from_env()


def get_low_level_docker_api():
    return docker.APIClient()


def parse_stream(out):
    data = json.loads(out)
    if "stream" in data:
        return data["stream"]
    elif "error" in data:
        return data["error"]
    else:
        return str(data)


def do_print(*args, name: str = None, quiet: bool = False) -> None:
    if not quiet:
        print(f"[parallel_docker_build{'' if name is None else f'|{name}'}]", *args)


def do_build(
    dockerfile: Union[Path, str],
    full_name: str,
    context: Union[Path, str] = None,
    rebuild: bool = False,
    quiet: bool = False,
    name: str = None,
) -> None:
    dockerfile = _absolute_file(dockerfile)
    context = _absolute_dir(context)
    do_print(f"Building {dockerfile} from context {context}", name=name, quiet=quiet)
    api = get_low_level_docker_api()
    name = full_name if name is None else f"{name}|{full_name}"
    if not str(dockerfile).startswith(str(context)):
        raise FileNotFoundError(
            f"Dockerfile ({dockerfile} is not in context: {context}"
        )
    _dockerfile = str(dockerfile.relative_to(context))
    if len(_dockerfile) == 0:
        raise ValueError(
            f"After striping context: ({context}) the dockerfile ({dockerfile}) "
            f"is blank: {_dockerfile}"
        )
    options = {
        "path": str(context),
        "dockerfile": _dockerfile,
        "tag": f"{full_name}:latest",
        "nocache": rebuild,
        "quiet": False,
    }
    do_print(f"Building: {options}", name=name, quiet=quiet)
    for out in api.build(**options):
        do_print(parse_stream(out).rstrip("\n"), name=name, quiet=quiet)


def do_push(full_name: str, tags: list, quiet: bool = False, name: str = None) -> None:
    api = get_high_level_docker_api()
    name = full_name if name is None else f"{name}|{full_name}"
    for tag in tags:
        do_print(f"Pushing: {full_name}:{tag}", name=name, quiet=quiet)
        api.images.push(full_name, tag=tag)


def make_image(
    dockerfile: Union[Path, str],
    organization: str,
    context: Union[Path, str] = None,
    allow_cross_platform: bool = False,
    push: bool = False,
    rebuild: bool = False,
    quiet: bool = False,
    name: str = None,
) -> None:
    # Handle paths
    dockerfile = _absolute_file(dockerfile)
    context = _absolute_dir(context)
    # Name for initial logging before the docker image full_name is known
    _name = (
        dockerfile.parent.stem if name is None else f"{name}|{dockerfile.parent.stem}"
    )
    # Parser full name and check platform
    extra_tags = [s.lstrip(".") for s in dockerfile.suffixes]
    for t in extra_tags:
        if t != t.lower():
            raise ValueError(
                f"Dockerfile suffix tags must all be lowercase: {dockerfile}"
            )
    image_arch = "x86_64"
    if "l4t" in extra_tags:
        do_print(f"Found Linux 4 Tegra tag in {dockerfile}", name=_name)
        image_arch = "aarch64"
    if "arm64v8" in extra_tags:
        do_print(f"Found ARM64v8 tag in {dockerfile}", name=_name)
        image_arch = "aarch64"
    if image_arch != platform.machine():
        if allow_cross_platform:
            do_print(
                "Attempting to build a cross platform image",
                f"(this={platform.machine()} vs requested={image_arch}):",
                f"{dockerfile}",
                name=_name,
            )
        else:
            do_print(
                "Cannot build across platforms without `-x` option",
                f"(this={platform.machine()} vs requested={image_arch}):",
                f"Skipping: {dockerfile}",
                name=_name,
            )
            return
    full_name = f"{organization}/{dockerfile.parent.stem}"
    if len(extra_tags):
        full_name += "_" + "_".join(extra_tags)
    # Build it
    do_build(
        dockerfile, full_name, context=context, rebuild=rebuild, quiet=quiet, name=name
    )
    # Push it
    if push:
        do_push(full_name, tags=["latest"], quiet=quiet, name=name)


def make_images(
    dockerfiles: Iterable[Union[Path, str]],
    organization: str,
    context: Path = None,
    max_num_workers: int = MAX_NUM_WORKERS,
    allow_cross_platform: bool = False,
    push: bool = False,
    rebuild: bool = False,
    quiet: bool = False,
    name: str = None,
) -> None:
    if len(dockerfiles) == 1 or max_num_workers == 1:
        for dockerfile in dockerfiles:
            make_image(
                dockerfile,
                organization,
                context=context,
                allow_cross_platform=allow_cross_platform,
                rebuild=rebuild,
                push=push,
                quiet=quiet,
                name=name,
            )
    else:
        results = []
        with multiprocessing.Pool(min(max_num_workers, len(dockerfiles))) as pool:
            for dockerfile in dockerfiles:
                do_print(f"Adding build job: {dockerfile}", name=name)
                results.append(
                    pool.apply_async(
                        make_image,
                        args=(dockerfile, organization),
                        kwds=dict(
                            context=context,
                            allow_cross_platform=allow_cross_platform,
                            rebuild=rebuild,
                            push=push,
                            quiet=quiet,
                            name=name,
                        ),
                    )
                )
            [r.wait() for r in results]


def get_dockerfiles_from_path(path: Union[str, Path] = None, name: str = None) -> list:
    path = _absolute_path(path)
    dockerfiles = []
    for p in list(path.rglob("**/Dockerfile*")) + list(path.rglob("Dockerfile*")):
        if p.is_dir():
            do_print(f"Skipping directory: {p}", name=name)
        else:
            dockerfiles.append(p)
    if len(dockerfiles) == 0:
        do_print(f"No `Dockerfile*`s found: {path}", name=name)
    do_print(f"Found {len(dockerfiles)} Dockerfiles here: {path}", name=name)
    return dockerfiles


def get_dockerfiles_from_paths(
    paths: Iterable[Union[str, Path]], name: str = None
) -> list:
    dockerfiles = []
    for path in paths:
        path = _absolute_path(path)
        if path.is_dir():
            dockerfiles.extend(get_dockerfiles_from_path(path, name=name))
        elif path.stem.startswith("Dockerfile"):
            dockerfiles.append(path)
        else:
            raise ValueError(f"Path is not a dockerfile: {path}")
    return dockerfiles


def validate_workflow_yaml(workflow: Union[Path, dict]) -> dict:
    """Validate workflow yaml file

    Parameters
    ----------
    workflow : Union[Path, dict]
        Workflow yaml path or loaded dictionary.

    Returns
    -------
    dict
        Validated workflow
    """
    # Load
    if isinstance(workflow, (Path, str)):
        data = yamale.make_data(path=_absolute_file(workflow))
    elif isinstance(workflow, dict):
        data = yamale.make_data(content=yaml.dump(workflow))
    else:
        raise ValueError(f"The workflow is not supported: {workflow}")
    schema = yamale.make_schema(WORKFLOW_SCHEMA_PATH)
    yamale.validate(schema, data)
    validated = data[0][0]
    # Defaults
    validated.setdefault("max_num_workers", 1)
    validated.setdefault("cross_platform", False)
    validated.setdefault("push", False)
    for stage in validated["stages"]:
        stage.setdefault("context", ".")
    return validated


def run_workflow(workflow: Path, rebuild: bool = False, quiet: bool = False) -> None:
    do_print(f"Loading: {workflow}")
    data = validate_workflow_yaml(workflow)
    for i, stage in enumerate(data["stages"]):
        name = f"{stage['name']} (Stage {i + 1} of {len(data['stages'])})"
        do_print("Starting run...", name=name)
        make_images(
            get_dockerfiles_from_paths(stage["paths"]),
            data["organization"],
            context=_absolute_dir(stage["context"]),
            max_num_workers=data["max_num_workers"],
            allow_cross_platform=data["cross_platform"],
            push=data["push"],
            rebuild=rebuild,
            quiet=quiet,
            name=name,
        )
    do_print(f"Workflow complete: {workflow}")
