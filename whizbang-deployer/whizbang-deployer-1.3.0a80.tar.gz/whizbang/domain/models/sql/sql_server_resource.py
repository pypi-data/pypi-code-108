from whizbang.domain.models.az_resource_base import AzResourceBase


class SqlServerResource(AzResourceBase):
    resource_group_name: str
