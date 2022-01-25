from datetime import datetime
from typing import Any, Dict, IO, List, Optional

import click
from click import ClickException
from pydantic import BaseModel, Field, root_validator
import tabulate
import yaml
from yaml.loader import SafeLoader

from anyscale.cli_logger import BlockLogger
from anyscale.cloud import get_cloud_id_and_name
from anyscale.cluster_compute import get_cluster_compute_from_name
from anyscale.controllers.base_controller import BaseController
from anyscale.sdk.anyscale_client.models.cluster_computes_query import (
    ClusterComputesQuery,
)
from anyscale.sdk.anyscale_client.models.clustercompute_list_response import (
    ClustercomputeListResponse,
)
from anyscale.sdk.anyscale_client.models.create_cluster_compute import (
    CreateClusterCompute,
)
from anyscale.sdk.anyscale_client.models.create_cluster_compute_config import (
    CreateClusterComputeConfig,
)
from anyscale.sdk.anyscale_client.models.text_query import TextQuery
from anyscale.util import get_endpoint


log = BlockLogger()  # Anyscale CLI Logger


class CreateClusterComputeConfigModel(BaseModel):
    """
    Schema for ClusterClusterCompute that is accepted from the CLI. Supports specifying
    `cloud` name instead of `cloud_id`, and preprocesses so fields have the correct
    values to call POST `/ext/v0/cluster_computes`.
    """

    cloud_id: Optional[str] = Field(
        None, description="The ID of the Anyscale cloud to use for launching Clusters.",
    )
    cloud: Optional[str] = Field(
        None,
        description="The name of the Anyscale cloud to use for launching Clusters.",
    )
    max_workers: Optional[int] = Field(
        None, description="Desired limit on total running workers for this Cluster."
    )

    allowed_azs: Optional[List[str]] = Field(
        None,
        description='The availability zones that clusters are allowed to be launched in, e.g. "us-west-2a". If not specified, any AZ may be used.',
    )

    head_node_type: Any = Field(
        ..., description="Node configuration to use for the head node. ",
    )

    worker_node_types: List[Any] = Field(
        ..., description="A list of node types to use for worker nodes. "
    )

    aws: Optional[Any] = Field(None, description="Fields specific to AWS node types.")

    gcp: Optional[Any] = Field(None, description="Fields specific to GCP node types.")

    azure: Optional[Any] = Field(
        None, description="Fields specific to Azure node types."
    )

    @root_validator
    def fill_cloud_id(cls: Any, values: Any) -> Any:  # noqa: N805
        cloud_id, cloud = (
            values.get("cloud_id"),
            values.get("cloud"),
        )
        if cloud_id and cloud:
            raise click.ClickException(
                "Only one of `cloud_id` or `cloud` can be provided in the cluster compute config file. "
            )
        if cloud:
            cloud_id, _ = get_cloud_id_and_name(
                api_client=None, cloud_id=None, cloud_name=cloud
            )
            values["cloud_id"] = cloud_id
        elif not cloud_id:
            raise click.ClickException(
                "Please provide either `cloud_id` or `cloud` in the cluster compute config file. "
            )
        return values


class ClusterComputeController(BaseController):
    """
    This controller powers functionalities related to Anyscale
    cluster compute configuration.
    """

    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log
        self.log.open_block("Output")

    def create(self, cluster_compute_file: IO[bytes], name: Optional[str]) -> None:
        """Builds a new cluster compute template
        If name is not provided, a default cluster-compute-name will be used and returned in the command output

        Information in output: Link to cluster compute in UI, cluster compute id
        """

        try:
            cluster_compute: Dict[str, Any] = yaml.load(
                cluster_compute_file, Loader=SafeLoader
            )
        except Exception as e:
            raise ClickException(f"Could not load cluster compute file: {e}")

        cluster_compute_config_model = CreateClusterComputeConfigModel(
            **cluster_compute
        )
        cluster_compute_config = CreateClusterComputeConfig(
            cloud_id=cluster_compute_config_model.cloud_id,
            max_workers=cluster_compute_config_model.max_workers,
            allowed_azs=cluster_compute_config_model.allowed_azs,
            region=None,
            head_node_type=cluster_compute_config_model.head_node_type,
            worker_node_types=cluster_compute_config_model.worker_node_types,
            aws=cluster_compute_config_model.aws,
            gcp=cluster_compute_config_model.gcp,
            azure=cluster_compute_config_model.azure,
        )
        if name is None:
            name = "cli-config-{}".format(datetime.now().isoformat())
        cluster_compute_response = self.anyscale_api_client.create_cluster_compute(
            CreateClusterCompute(name=name, config=cluster_compute_config)
        )
        created_cluster_compute = cluster_compute_response.result
        cluster_compute_id = created_cluster_compute.id
        cluster_compute_name = created_cluster_compute.name
        url = get_endpoint(f"/configurations/cluster-computes/{cluster_compute_id}")
        log.info(f"View this cluster compute at: {url}")
        log.info(f"Cluster compute id: {cluster_compute_id}")
        log.info(f"Cluster compute name: {cluster_compute_name}")

    def delete(self, cluster_compute_name: Optional[str], id: Optional[str]) -> None:
        """Deletes the cluster compute with the given name or id.
        Exactly one of cluster_compute_name or id must be provided.
        """

        if int(bool(cluster_compute_name)) + int(bool(id)) != 1:
            raise ClickException(
                "Not deleted. Please provide exactly one of: cluster compute name, id."
            )

        if id:
            self.anyscale_api_client.get_cluster_compute(id)
            cluster_compute_id = id
        else:
            # find the cluster compute id from the name
            query = ClusterComputesQuery(name=TextQuery(equals=cluster_compute_name))
            query_response: ClustercomputeListResponse = self.anyscale_api_client.search_cluster_computes(
                query
            )
            cluster_results = query_response.results
            if len(cluster_results) != 1:
                raise ClickException(
                    f"Not deleted. No cluster compute template exists with the name {cluster_compute_name}."
                )
            cluster_compute_id = cluster_results[0].id
        self.anyscale_api_client.delete_cluster_compute(cluster_compute_id)
        log.info("Cluster compute deleted.")

    def list(
        self,
        cluster_compute_name: Optional[str],
        cluster_compute_id: Optional[str],
        include_shared: bool,
        max_items: int,
    ) -> None:
        cluster_compute_list = []
        if cluster_compute_id:
            cluster_compute_list = [
                self.anyscale_api_client.get_cluster_compute(cluster_compute_id).result
            ]
        elif cluster_compute_name:
            cluster_compute_list = self.anyscale_api_client.search_cluster_computes(
                {"name": {"equals": cluster_compute_name}, "paging": {"count": 1}}
            ).results
        else:
            creator_id = (
                self.api_client.get_user_info_api_v2_userinfo_get().result.id
                if not include_shared
                else None
            )
            resp = self.anyscale_api_client.search_cluster_computes(
                {"creator_id": creator_id, "paging": {"count": 20}}
            )
            cluster_compute_list.extend(resp.results)
            paging_token = resp.metadata.next_paging_token
            has_more = (paging_token is not None) and (
                len(cluster_compute_list) < max_items
            )
            while has_more:
                resp = self.anyscale_api_client.search_cluster_computes(
                    {
                        "creator_id": creator_id,
                        "paging": {"count": 20, "paging_token": paging_token},
                    }
                )
                cluster_compute_list.extend(resp.results)
                paging_token = resp.metadata.next_paging_token
                has_more = (paging_token is not None) and (
                    len(cluster_compute_list) < max_items
                )
            cluster_compute_list = cluster_compute_list[:max_items]

        cluster_compute_table = [
            [
                cluster_compute.id,
                cluster_compute.name,
                self.anyscale_api_client.get_cloud(
                    cluster_compute.config.cloud_id
                ).result.name
                if cluster_compute.config.cloud_id
                else None,
                cluster_compute.last_modified_at.strftime("%m/%d/%Y, %H:%M:%S"),
                get_endpoint(f"configurations/cluster-computes/{cluster_compute.id}"),
            ]
            for cluster_compute in cluster_compute_list
        ]

        table = tabulate.tabulate(
            cluster_compute_table,
            headers=["ID", "NAME", "CLOUD", "LAST MODIFIED AT", "URL"],
            tablefmt="plain",
        )
        print(f"Cluster computes:\n{table}")

    def get(
        self, cluster_compute_name: Optional[str], cluster_compute_id: Optional[str],
    ) -> None:
        if (
            int(cluster_compute_name is not None) + int(cluster_compute_id is not None)
            != 1
        ):
            raise click.ClickException(
                "Please only provide one of `cluster-compute-name` or `--id`."
            )
        if cluster_compute_name:
            cluster_compute_id = get_cluster_compute_from_name(
                cluster_compute_name, self.api_client
            ).id
        config = self.api_client.get_compute_template_api_v2_compute_templates_template_id_get(
            cluster_compute_id
        ).result.config
        # TODO(nikita): Improve formatting here
        print(config)
