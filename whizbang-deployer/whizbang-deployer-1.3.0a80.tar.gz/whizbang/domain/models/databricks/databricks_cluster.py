class DatabricksCluster:
    def __init__(self, cluster_dict: dict):
        self.cluster_dict = cluster_dict

    @property
    def cluster_name(self) -> str: return self.cluster_dict['cluster_name']
