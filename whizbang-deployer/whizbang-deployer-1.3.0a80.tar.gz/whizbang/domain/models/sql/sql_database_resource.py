from whizbang.domain.models.az_resource_base import AzResourceBase


class SqlServerDatabaseResource(AzResourceBase):
    server: str
