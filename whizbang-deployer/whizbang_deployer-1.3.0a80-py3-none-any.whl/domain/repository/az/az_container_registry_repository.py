from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase


class AzContainerRegistryRepository(AzRepositoryBase):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str:
        return 'acr'

    def get_tags(self, registry_name: str, repository_name: str, subscription: str):
        return self._execute(f'repository show-tags'
                             f' --name {registry_name}'
                             f' --repository {repository_name}'
                             f' --subscription {subscription}').results
