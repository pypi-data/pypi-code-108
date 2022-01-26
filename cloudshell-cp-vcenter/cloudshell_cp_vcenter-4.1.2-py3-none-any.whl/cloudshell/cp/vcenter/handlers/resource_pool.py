from pyVmomi import vim

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.handlers.managed_entity_handler import ManagedEntityHandler


class ResourcePoolNotFound(BaseVCenterException):
    def __init__(self, entity: ManagedEntityHandler, name: str):
        self.name = name
        self.entity = entity
        super().__init__(f"Resource Pool with name {name} not found in the {entity}")


class ResourcePoolHandler(ManagedEntityHandler):
    _entity: vim.ResourcePool

    def __str__(self) -> str:
        return f"Resource Pool '{self.name}'"
