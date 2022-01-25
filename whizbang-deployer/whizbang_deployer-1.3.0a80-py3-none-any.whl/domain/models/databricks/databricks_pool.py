class DatabricksPool:
    def __init__(self, pool_dict: dict):
        self.pool_dict = pool_dict

    @property
    def pool_name(self) -> str: return self.pool_dict['instance_pool_name']
