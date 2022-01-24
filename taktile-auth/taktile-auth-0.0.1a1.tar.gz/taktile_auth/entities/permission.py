import re
import typing as t

import pydantic

from taktile_auth.entities.resource import (
    RESOURCES,
    Resource,
    ResourceDefinition,
)
from taktile_auth.enums import Action


class Permission(pydantic.BaseModel):
    actions: t.Set[Action]
    resource: Resource

    def __contains__(self, query: "Permission") -> bool:
        action_match = query.actions.difference(self.actions) == set()
        resource_match = True
        for field in self.resource.dict().keys():
            allowed = getattr(self.resource, field)
            queried = getattr(query.resource, field)
            if not re.fullmatch(
                allowed.replace("*", ".*"), queried
            ):  # Beware of regex fails
                resource_match = False
                break
        return action_match and resource_match


Permission.update_forward_refs()


class PermissionDefinition(pydantic.BaseModel):
    actions: t.Set[Action]
    resource_definition: ResourceDefinition

    def render(self, values: t.Dict[str, str]) -> Permission:
        return Permission(
            actions=self.actions,
            resource=self.resource_definition.get_resource()(**values),
        )


def create_query(query: str) -> Permission:
    action_str, _, res_str = query.partition(":")
    resource_name, _, args_str = res_str.partition("/")
    actions = action_str.split("+")
    args = args_str.split(",")
    fields = list(RESOURCES[resource_name].args.keys())
    resource_vals = {fields[x]: args[x] for x in range(len(fields))}
    return Permission(
        actions=set(actions),
        resource=RESOURCES[resource_name].get_resource()(**resource_vals),
    )
