"""
Functionality for formatting output strings for Clouds
"""
import json
from typing import List

import tabulate

from anyscale.client.openapi_client.models.cloud import Cloud


def format_clouds_output(clouds: List[Cloud], json_format: bool) -> str:
    return (
        format_clouds_output_json(clouds=clouds)
        if json_format
        else format_clouds_output_table(clouds=clouds)
    )


def format_clouds_output_json(clouds: List[Cloud]) -> str:
    cloud_jsons = []
    for cloud in clouds:
        cloud_jsons.append(
            {
                "id": cloud.id,
                "name": cloud.name,
                "provider": cloud.provider,
                "region": cloud.region,
                "credentials": cloud.credentials,
            }
        )
    return json.dumps(cloud_jsons)


def format_clouds_output_table(clouds: List[Cloud]) -> str:
    table_rows = []
    for cloud in clouds:
        table_rows.append(
            [cloud.id, cloud.name, cloud.provider, cloud.region, cloud.credentials]
        )
    table = tabulate.tabulate(
        table_rows,
        headers=["ID", "name", "PROVIDER", "REGION", "CREDENTIALS"],
        tablefmt="plain",
    )

    return f"Clouds:\n{table}"
