class DatabricksSecretScope:
    def __init__(self, keyvault_name, keyvault_resource_id, keyvault_dns=None):
        self.keyvault_dns = keyvault_dns
        self.keyvault_name = keyvault_name
        self.keyvault_resource_id = keyvault_resource_id