from typing import List, Optional
from dependency_injector.providers import ConfigurationOption
from pydantic import BaseModel

from whizbang.domain.models.keyvault.keyvault_access_policy import KeyVaultAccessPolicy
from whizbang.domain.models.rbac_policy import RBACPolicy


# Consider defining this is a data class
class EnvironmentConfig(BaseModel):
    subscription_id: Optional[str]
    """The subscription of the target deployment."""
    
    tenant_id: Optional[str]
    """The tenant id of the target deployment."""
    
    resource_group_name: Optional[str]
    """The name of the resource group to be deployed to."""
    
    resource_group_location: Optional[str]
    """The location (Azure datacenter) of the target deployment."""

    # Nested Fields below
    rbac_policies: Optional[List[RBACPolicy]] = []
    """A list of all RBAC policies in the solution."""

    keyvault_access_policies: Optional[List[KeyVaultAccessPolicy]] = []
    """A list of all KeyVault Access policies in the solution."""
    
    properties: Optional[dict] = {}
    """A bag of all of the configuration that was used to create the base class, but it also exposes the solution specifici customizations."""