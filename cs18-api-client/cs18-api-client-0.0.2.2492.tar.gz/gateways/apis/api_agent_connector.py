from typing import List

from gateways.apis.api_base_class import ApiBase


class ApiAgentConnector(ApiBase):
    def get_k8s_cluster_agents(self, cluster_id: str):
        return self.build_route(f"agent/cluster/status?cluster_id={cluster_id}")
