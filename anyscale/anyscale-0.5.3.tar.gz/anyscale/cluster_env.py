import sys
from typing import List, Optional

import click
from packaging import version
import ray

from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.connect import MINIMUM_RAY_VERSION
from anyscale.sdk.anyscale_client import ClusterEnvironmentBuild
from anyscale.util import get_endpoint


log = BlockLogger()


def get_default_cluster_env_build(
    api_client: Optional[DefaultApi] = None,
    anyscale_api_client: Optional[DefaultApi] = None,
) -> ClusterEnvironmentBuild:
    # TODO(nikita): Condense with anyscale.connect after unifying logging.
    if api_client is None:
        api_client = get_auth_api_client().api_client
    if anyscale_api_client is None:
        anyscale_api_client = get_auth_api_client().anyscale_api_client

    py_version = "".join(str(x) for x in sys.version_info[0:2])
    if py_version not in ["36", "37", "38"]:
        raise ValueError(
            "No default cluster env for python version {}. Please use a version of python between 3.6 and 3.8.".format(
                py_version
            )
        )
    ray_version = ray.__version__
    if version.parse(ray_version) < version.parse(MINIMUM_RAY_VERSION):
        raise ValueError(
            f"No default cluster env for Ray version {ray_version}. Please upgrade "
            f'to a version >= {MINIMUM_RAY_VERSION} with `pip install "ray>={MINIMUM_RAY_VERSION}"`.'
        )
    if "dev0" in ray_version:
        raise ValueError(
            f"Your locally installed Ray version is {ray_version}. "
            "There is no default cluster environments for nightly versions of Ray."
        )
    try:
        build_id = api_client.get_default_cluster_env_build_api_v2_builds_default_py_version_ray_version_get(
            f"py{py_version}", ray_version
        ).result.id
        build = anyscale_api_client.get_cluster_environment_build(build_id).result
        return build
    except Exception:
        raise RuntimeError(
            f"Failed to get default cluster env for Ray: {ray_version} on Python: py{py_version}"
        )


def get_build_from_cluster_env_identifier(
    cluster_env_identifier: str, anyscale_api_client: Optional[DefaultApi] = None,
) -> ClusterEnvironmentBuild:
    """
    Get a build id from a cluster environment identifier of form `my_cluster_env:1` or
    `my_cluster_env`. If no build revision is specified, return id of latest build
    for this application config.

    TODO(nikita): Move this to behind api endpoint and consolidate with anyscale.connect
    """

    if anyscale_api_client is None:
        anyscale_api_client = get_auth_api_client().anyscale_api_client
    try:
        components = cluster_env_identifier.rsplit(":", 1)
        cluster_env_name = components[0]
        cluster_env_revision = int(components[1]) if len(components) > 1 else None
    except ValueError:
        raise click.ClickException(
            "Invalid cluster-env-name provided. Please make sure the provided name is of "
            "the form <cluster-env-name>:<revision>. For example, `my_cluster_env:1`."
        )

    # ID of cluster env and not build itself
    cluster_env_id = get_cluster_env_from_name(cluster_env_name, anyscale_api_client).id

    builds = list_builds(cluster_env_id, anyscale_api_client)
    if cluster_env_revision:
        for build in builds:
            if build.revision == cluster_env_revision:
                return build

        raise click.ClickException(
            "Revision {} of cluster environment '{}' not found.".format(
                cluster_env_revision, cluster_env_name
            )
        )
    else:
        latest_build_revision = -1
        build_to_use = None
        for build in builds:
            if build.revision > latest_build_revision:
                latest_build_revision = build.revision
                build_to_use = build

        if not build_to_use:
            raise click.ClickException(
                "Error finding latest build of cluster environment {}. Please manually "
                "specify the build version in the cluster environment name with the format "
                "<cluster-env-name>:<revision>. For example, `my_cluster_env:1`.".format(
                    cluster_env_name
                )
            )
        return build_to_use


def get_cluster_env_from_name(
    cluster_env_name: str, anyscale_api_client: Optional[DefaultApi] = None,
) -> ClusterEnvironmentBuild:
    """
    Get id of the cluster env (not build) given the name.
    """

    if anyscale_api_client is None:
        anyscale_api_client = get_auth_api_client().anyscale_api_client
    cluster_envs = anyscale_api_client.search_cluster_environments(
        {"name": {"equals": cluster_env_name}, "paging": {"count": 1}}
    ).results
    for cluster_env in cluster_envs:
        if cluster_env.name == cluster_env_name:
            return cluster_env

    raise click.ClickException(
        "Cluster environment '{}' not found. ".format(cluster_env_name)
    )


def list_builds(
    cluster_env_id: str,
    anyscale_api_client: Optional[DefaultApi] = None,
    max_items: Optional[int] = None,
) -> List[ClusterEnvironmentBuild]:
    """
    List all builds for a given cluster env id.
    """

    if anyscale_api_client is None:
        anyscale_api_client = get_auth_api_client().anyscale_api_client
    entities: List[ClusterEnvironmentBuild] = []
    has_more = (len(entities) < max_items) if max_items else True
    while has_more:
        resp = anyscale_api_client.list_cluster_environment_builds(
            cluster_env_id, count=50, paging_token=None
        )
        entities.extend(resp.results)
        paging_token = resp.metadata.next_paging_token
        has_more = paging_token is not None
        if max_items:
            has_more = has_more and (len(entities) < max_items)
    if max_items:
        return entities[:max_items]
    else:
        return entities


def validate_successful_build(
    build_id: str, anyscale_api_client: Optional[DefaultApi] = None,
) -> None:
    """
    Validate build_id provided is of a successfully completed build.
    """

    if anyscale_api_client is None:
        anyscale_api_client = get_auth_api_client().anyscale_api_client
    build = anyscale_api_client.get_cluster_environment_build(build_id).result
    if build.status != "succeeded":
        cluster_env = anyscale_api_client.get_cluster_environment(
            build.cluster_environment_id
        ).result
        raise click.ClickException(
            f"The cluster environment build {cluster_env.name}:{build.revision} currently is in state: {build.status}. "
            f'More information about this build can be viewed at {get_endpoint(f"configurations/app-config-details/{build_id}")}. '
            "Please provide a cluster environment that has already been built successfully."
        )
