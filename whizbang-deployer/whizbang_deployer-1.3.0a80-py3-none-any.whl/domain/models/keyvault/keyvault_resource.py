from whizbang.domain.models.az_resource_base import AzResourceBase


class KeyVaultResource(AzResourceBase):
    def __init__(self, resource_name, resource_group_name, location):
        AzResourceBase.__init__(
            self,
            resource_name=resource_name,
            resource_group_name=resource_group_name,
            location=location
        )
