from typing import List

from pydantic import BaseModel


class KeyVaultAccessPolicyPermissions(BaseModel):
    storage: List[str] = []
    certificates: List[str] = []
    secrets: List[str] = []
    keys: List[str] = []


class KeyVaultAccessPolicy(BaseModel):
    permissions: KeyVaultAccessPolicyPermissions
    lookup_value: str = None
    lookup_type: str = None
    object_id: str = None
    name: str = None
    resource_group_name: str = None
    keyvault_name: str
