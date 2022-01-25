from typing import Any, cast, Dict, List, Optional, Tuple

import click
from click import ClickException
from openapi_client.rest import ApiException

from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.sdk.anyscale_client.models.cloud import Cloud


log = BlockLogger()


def get_cloud_json_from_id(cloud_id: str, api_client: DefaultApi) -> Dict["str", Any]:
    try:
        cloud = api_client.get_cloud_api_v2_clouds_cloud_id_get(
            cloud_id=cloud_id
        ).result
    except ApiException:
        return {
            "error": {
                "cloud_id": cloud_id,
                "message": f"The cloud with id, {cloud_id} has been deleted. Please create a new cloud with `anyscale cloud setup`.",
            }
        }
    return {
        "id": cloud.id,
        "name": cloud.name,
        "provider": cloud.provider,
        "region": cloud.region,
        "credentials": cloud.credentials,
        "config": cloud.config,
    }


def get_cloud_id_and_name(
    api_client: Optional[DefaultApi] = None,
    cloud_id: Optional[str] = None,
    cloud_name: Optional[str] = None,
) -> Tuple[str, str]:
    if api_client is None:
        api_client = get_auth_api_client().api_client
    if cloud_id and cloud_name:
        raise ClickException(
            "Both '--cloud-id' and '--cloud-name' specified. Please only use one."
        )
    elif cloud_name:
        resp_get_cloud = api_client.find_cloud_by_name_api_v2_clouds_find_by_name_post(
            cloud_name_options={"name": cloud_name}
        )
        cloud = resp_get_cloud.result
    elif cloud_id:
        resp_get_cloud = api_client.get_cloud_api_v2_clouds_cloud_id_get(
            cloud_id=cloud_id
        )

        cloud = resp_get_cloud.result
    else:
        try:
            clouds = api_client.list_clouds_api_v2_clouds_get().results
        except Exception as e:
            if (isinstance(e, ApiException) and e.status == 404) or (  # type: ignore
                isinstance(e, ClickException) and "Reason: 404" in str(e)
            ):
                # No clouds
                raise ClickException(
                    'There are no clouds assigned to your account. Please create a cloud using "anyscale cloud setup".'
                )
            raise e

        if len(clouds) == 0:
            # No clouds
            raise ClickException(
                'There are no clouds assigned to your account. Please create a cloud using "anyscale cloud setup".'
            )

        if len(clouds) > 1:
            raise ClickException(
                "Multiple clouds: {}\n"
                "Please specify the one you want to refer to using --cloud-name.".format(
                    [cloud.name for cloud in clouds]
                )
            )
        cloud = clouds[0]
    return cloud.id, cloud.name


def get_last_used_cloud(
    project_id: Optional[str], anyscale_api_client: Optional[DefaultApi] = None
) -> str:
    """Return the name of the cloud last used in the project.

    Args:
        project_id (str): The project to get the last used cloud for.

    Returns:
        Name of the cloud last used in this project.

    TODO(nikita): Condense with anyscale.connect after unifying logging.
    """
    if anyscale_api_client is None:
        anyscale_api_client = get_auth_api_client().anyscale_api_client
    if project_id:
        cloud_id = anyscale_api_client.get_project(project_id).result.last_used_cloud_id
    else:
        cloud_id = None
    if cloud_id:
        try:
            cloud = anyscale_api_client.get_cloud(cloud_id).result
        except Exception:
            raise click.ClickException(
                f"Failed to fetch Cloud with id: {cloud_id}. Please specify cloud_name in the command."
            )
    else:
        # TODO(nikita): Add some logics or checks here so users don't start clusters with clouds
        # they don't intend to.
        clouds = get_all_clouds()
        if len(clouds) > 0:
            # Clouds are sorted in descending order, pick the oldest one as default.
            cloud = clouds[-1]
        else:
            raise click.ClickException(
                "No cloud configured, please set up a cloud with 'anyscale cloud setup'."
            )

    cloud_name = cloud.name
    log.info(
        (
            f"Using last active cloud '{cloud_name}'. "
            "Specify cloud_name in the command to overwrite."
        )
    )
    return cast(str, cloud_name)


def get_all_clouds(anyscale_api_client: Optional[DefaultApi] = None) -> List[Cloud]:
    """Fetches all Clouds the user has access to.
    Returns:
        List of all Clouds the user has access to.

    TODO(nikita): Condense with anyscale.connect after unifying logging.
    """
    if anyscale_api_client is None:
        anyscale_api_client = get_auth_api_client().anyscale_api_client

    cloud_list_response = anyscale_api_client.search_clouds({"paging": {"count": 50}})
    all_clouds = cloud_list_response.results
    next_paging_token = cloud_list_response.metadata.next_paging_token

    while next_paging_token:
        cloud_list_response = anyscale_api_client.search_clouds(
            {"paging": {"count": 50, "paging_token": next_paging_token}}
        )
        next_paging_token = cloud_list_response.metadata.next_paging_token
        all_clouds.extend(cloud_list_response.results)

    return all_clouds  # type: ignore
