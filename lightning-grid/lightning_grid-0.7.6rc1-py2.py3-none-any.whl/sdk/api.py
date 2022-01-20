from dataclasses import dataclass
from typing import List

from grid.openapi import Externalv1Cluster, V1InstanceType
from grid.sdk.client import create_swagger_client
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.clusters import list_clusters as rest_list_clusters

__all__ = ["get_instance_types", "list_clusters"]


def get_instance_types(cluster_id: str) -> List[V1InstanceType]:
    """
    Get the instance types for the given cluster
    """
    api_client = GridRestClient(create_swagger_client())
    resp = api_client.cluster_service_list_cluster_instance_types(id=cluster_id)
    return resp.instance_types


@dataclass
class ListClusters:
    default_cluster: str
    clusters: List[Externalv1Cluster]


# TODO - move this to sdk/clusters.py
def list_clusters(is_global: bool = False) -> ListClusters:
    """
    List the clusters for the user

    Parameters
    ----------
    is_global:
        Only returns global clusters
    """
    c = GridRestClient(create_swagger_client())
    resp = rest_list_clusters(c, is_global=is_global)
    return ListClusters(default_cluster=resp.default_cluster, clusters=resp.clusters if resp.clusters else [])
