from whizbang.domain.models.az_resource_base import AzResourceBase


class StorageAccountResource(AzResourceBase):
    # todo: add various storage account options
    pass


class StorageContainer:
    def __init__(self, container_name, storage_account_name, account_key=None):
        self.container_name = container_name
        self.storage_account_name = storage_account_name
        self.account_key = account_key


class StorageSource:
    def __init__(self, local_path, container_name, storage_account_name):
        self.local_path = local_path
        self.container_name = container_name
        self.storage_account_name = storage_account_name


class StorageBlobSource(StorageSource):
    def __init__(self, local_path, container_name, storage_account_name, name=None):
        self.name = name
        StorageSource.__init__(self,
                               local_path=local_path,
                               container_name=container_name,
                               storage_account_name=storage_account_name)


class StorageDatalakeSource(StorageSource):
    def __init__(self, local_path, container_name, storage_account_name):
        StorageSource.__init__(self,
                               local_path=local_path,
                               container_name=container_name,
                               storage_account_name=storage_account_name)

