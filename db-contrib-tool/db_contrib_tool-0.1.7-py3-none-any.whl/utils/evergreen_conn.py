"""Helper functions to interact with evergreen."""
import os
import pathlib
from typing import List, Optional

import structlog
from evergreen import RetryingEvergreenApi, Version
from requests import HTTPError

EVERGREEN_HOST = "https://evergreen.mongodb.com"
EVERGREEN_CONFIG_LOCATIONS = (
    # Common for machines in Evergreen
    os.path.join(os.getcwd(), ".evergreen.yml"),
    # Common for local machines
    os.path.expanduser(os.path.join("~", ".evergreen.yml")),
)

LOGGER = structlog.getLogger(__name__)


class EvergreenConnError(Exception):
    """Errors in evergreen_conn.py."""

    pass


def _find_evergreen_yaml_candidates() -> List[str]:
    # Common for machines in Evergreen
    candidates = [os.getcwd()]

    cwd = pathlib.Path(os.getcwd())
    # add every path that is the parent of CWD as well
    for parent in cwd.parents:
        candidates.append(parent)

    # Common for local machines
    candidates.append(os.path.expanduser(os.path.join("~", ".evergreen.yml")))

    out = []
    for path in candidates:
        file = os.path.join(path, ".evergreen.yml")
        if os.path.isfile(file):
            out.append(file)

    return out


def get_evergreen_api(evergreen_config=None):
    """Return evergreen API."""
    if evergreen_config:
        possible_configs = [evergreen_config]
    else:
        possible_configs = _find_evergreen_yaml_candidates()

    if not possible_configs:
        LOGGER.error("Could not find .evergreen.yml", candidates=possible_configs)
        raise RuntimeError("Could not find .evergreen.yml")

    last_ex = None
    for config in possible_configs:
        try:
            return RetryingEvergreenApi.get_api(config_file=config)
        except Exception as ex:
            last_ex = ex
            continue

    LOGGER.error(
        "Could not connect to Evergreen with any .evergreen.yml files available on this system",
        config_file_candidates=possible_configs,
    )
    raise last_ex


def get_buildvariant_name(config, edition, platform, architecture, major_minor_version):
    """Return Evergreen buildvariant name."""

    buildvariant_name = ""
    evergreen_buildvariants = config.evergreen_buildvariants

    for buildvariant in evergreen_buildvariants:
        if (
            buildvariant.edition == edition
            and buildvariant.platform == platform
            and buildvariant.architecture == architecture
        ):
            versions = buildvariant.versions
            if major_minor_version in versions:
                buildvariant_name = buildvariant.name
                break
            elif not versions:
                buildvariant_name = buildvariant.name

    return buildvariant_name


def get_evergreen_projects(evg_api: RetryingEvergreenApi) -> List[str]:
    """Return the list of mongodb/mongo evergreen project identifiers."""
    evg_projects = [
        proj
        for proj in evg_api.all_projects()
        if proj.enabled and "mongodb-mongo-" in proj.identifier
    ]
    return [proj.identifier for proj in evg_projects]


def get_evergreen_version(
    evergreen_projects: List[str], evg_api: RetryingEvergreenApi, evg_ref: str
) -> Optional[Version]:
    """Return evergreen version by reference (commit_hash or evergreen_version_id)."""
    # Evergreen reference as evergreen_version_id
    evg_refs = [evg_ref]
    # Evergreen reference as {project_name}_{commit_hash}
    evg_refs.extend(f"{proj.replace('-', '_')}_{evg_ref}" for proj in evergreen_projects)

    for ref in evg_refs:
        try:
            evg_version = evg_api.version_by_id(ref)
        except HTTPError:
            continue
        else:
            LOGGER.debug(
                "Found evergreen version.",
                evergreen_version=f"{EVERGREEN_HOST}/version/{evg_version.version_id}",
            )
            return evg_version

    return None


def get_evergreen_versions(evg_api, evg_project):
    """Return the list of evergreen versions by evergreen project name."""
    return evg_api.versions_by_project(evg_project)


def get_compile_artifact_urls(evg_api, evg_version, buildvariant_name, ignore_failed_push=False):
    """Return compile urls from buildvariant in Evergreen version."""
    try:
        build_id = evg_version.build_variants_map[buildvariant_name]
    except KeyError:
        raise EvergreenConnError(f"Buildvariant {buildvariant_name} not found.")

    evg_build = evg_api.build_by_id(build_id)
    LOGGER.debug("Found evergreen build.", evergreen_build=f"{EVERGREEN_HOST}/build/{build_id}")
    evg_tasks = evg_build.get_tasks()
    tasks_wrapper = _filter_successful_tasks(evg_tasks)

    # Ignore push tasks if specified as such, else return no results if push does not exist.
    if ignore_failed_push:
        tasks_wrapper.push_task = None
    elif tasks_wrapper.push_task is None:
        return {}

    return _get_multiversion_urls(tasks_wrapper)


def _get_multiversion_urls(tasks_wrapper):
    compile_artifact_urls = {}

    binary = tasks_wrapper.binary_task
    push = tasks_wrapper.push_task
    symbols = tasks_wrapper.symbols_task

    required_tasks = [binary, push] if push is not None else [binary]

    if all(task and task.status == "success" for task in required_tasks):
        LOGGER.info(
            "Required evergreen task(s) were successful.",
            required_tasks=f"{required_tasks}",
            task_id=f"{EVERGREEN_HOST}/task/{required_tasks[0].task_id}",
        )
        evg_artifacts = binary.artifacts
        for artifact in evg_artifacts:
            compile_artifact_urls[artifact.name] = artifact.url

        if symbols and symbols.status == "success":
            for artifact in symbols.artifacts:
                compile_artifact_urls[artifact.name] = artifact.url
        elif symbols and symbols.task_id:
            LOGGER.warning(
                "debug symbol archive was unsuccessful",
                archive_symbols_task=f"{EVERGREEN_HOST}/task/{symbols.task_id}",
            )

        # Tack on the project id for generating a friendly decompressed name for the artifacts.
        compile_artifact_urls["project_identifier"] = binary.project_identifier

    elif all(task for task in required_tasks):
        LOGGER.warning(
            "Required Evergreen task(s) were not successful.",
            required_tasks=f"{required_tasks}",
            task_id=f"{EVERGREEN_HOST}/task/{required_tasks[0].task_id}",
        )
    else:
        LOGGER.error("There are no `compile` and/or 'push' tasks in the evergreen build")

    return compile_artifact_urls


class _MultiversionTasks(object):
    """Tasks relevant for multiversion setup."""

    def __init__(self, symbols, binary, push):
        """Init function."""
        self.symbols_task = symbols
        self.binary_task = binary
        self.push_task = push


def _filter_successful_tasks(evg_tasks) -> _MultiversionTasks:
    compile_task = None
    archive_symbols_task = None
    push_task = None
    for evg_task in evg_tasks:
        # Only set the compile task if there isn't one already, otherwise
        # newer tasks like "archive_dist_test_debug" take precedence.
        if evg_task.display_name in ("compile", "archive_dist_test") and compile_task is None:
            compile_task = evg_task
        elif evg_task.display_name == "push":
            push_task = evg_task
        elif evg_task.display_name == "archive_dist_test_debug":
            archive_symbols_task = evg_task
        if compile_task and push_task and archive_symbols_task:
            break
    return _MultiversionTasks(symbols=archive_symbols_task, binary=compile_task, push=push_task)
