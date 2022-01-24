import typing as t

import pydantic
import yaml

from taktile_auth.entities.permission import (
    Permission,
    PermissionDefinition,
    create_query,
)
from taktile_auth.entities.resource import RESOURCES, Resource
from taktile_auth.enums import Action


class Role(pydantic.BaseModel):
    name: str
    permissions: t.List[Permission]
    children: t.List["Role"]

    def is_allowed(self, query: str) -> bool:
        query_permission = create_query(query)
        for permission in self.permissions:
            if query_permission in permission:
                return True
        return False

    def get_all_permissions(self) -> t.Set[str]:
        allowed: t.Set[str] = set()
        for perm in self.permissions:
            actions = "+".join(sorted(perm.actions))
            resource_name = type(perm.resource).__name__
            vals = ",".join(perm.resource.dict().values())
            allowed.add(f"{actions}:{resource_name}/{vals}")
        return allowed


Role.update_forward_refs()


class RoleDefinition(pydantic.BaseModel):
    name: str
    permission_definitions: t.List[PermissionDefinition]
    args: t.List[str]
    children: t.List["RoleDefinition"]

    @classmethod
    def from_yaml(
        cls: "RoleDefinition", role_name: str, role_yaml: t.Dict[str, t.Any]
    ) -> "RoleDefinition":
        permissions = []
        children = []
        role_args: str = role_yaml[role_name]["role_args"]
        role_body: t.List[str] = role_yaml[role_name]["role_body"]
        for clause in role_body:
            if ":" in clause:  # Permission
                action_str, _, resource_str = clause.partition(":")
                actions = action_str.split("+")
                resource_name, _, args_str = resource_str.partition("/")
                # TODO - Validate if it matches the resources defined
                # resource_args = args_str.split(",")
                permissions.append(
                    PermissionDefinition(
                        actions=set(actions),
                        resource_definition=RESOURCES[resource_name],
                    )
                )
            else:  # Sub Role
                sub_role, sep, sub_role_args_str = clause.partition("/")
                children.append(RoleDefinition.from_yaml(sub_role, role_yaml))
        return RoleDefinition(
            name=role_name,
            permission_definitions=permissions,
            args=role_args,
            children=children,
        )

    def render(self, values: t.List[str]) -> Role:
        vals = {
            self.args[x]: values[x]
            for x in range(min(len(self.args), len(values)))
        }
        # Flattening Permissions to include those from Children
        permission_map: t.Dict[Resource, t.Set[Action]] = {}
        for permission_definition in self.permission_definitions:
            permission = permission_definition.render(vals)
            if permission.resource not in permission_map:
                permission_map[permission.resource] = permission.actions
            else:
                permission_map[permission.resource] = permission_map[
                    permission.resource
                ].union(permission.actions)
        children = []
        for child_definition in self.children:
            child = child_definition.render(list(vals.values()))
            children.append(child)
            for permission in child.permissions:
                if permission.resource not in permission_map:
                    permission_map[permission.resource] = permission.actions
                else:
                    permission_map[permission.resource] = permission_map[
                        permission.resource
                    ].union(permission.actions)
        permissions = []
        for resource, actions in permission_map.items():
            permissions.append(Permission(actions=actions, resource=resource))
        return Role(name=self.name, permissions=permissions, children=children)


RoleDefinition.update_forward_refs()

ROLES: t.Dict[str, RoleDefinition] = {}
# TODO - Add Load Functions
_ROLE_YAML = {}
with open("assets/roles.yaml", "rb") as f:  # TODO - Use Pathlib
    roles = yaml.safe_load(f)
for role_signature, role_body in roles.items():
    role_name, sep, role_args_str = role_signature.partition("/")
    role_args = role_args_str.split(",")
    _ROLE_YAML[role_name] = {"role_args": role_args, "role_body": role_body}

for role_name in _ROLE_YAML.keys():
    ROLES[role_name] = RoleDefinition.from_yaml(role_name, _ROLE_YAML)
