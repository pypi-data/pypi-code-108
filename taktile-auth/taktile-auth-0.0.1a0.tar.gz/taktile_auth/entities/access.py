import typing as t

from taktile_auth.entities.role import ROLES, Role


class Access:
    roles: t.List[Role] = []
    # TODO - Simplify the roles param

    def __init__(self, roles: t.List[t.Tuple[str, t.List[str]]]) -> None:
        for role_name, args in roles:
            self.roles.append(ROLES[role_name].render(args))

    def get_all_permissions(self) -> t.Set[str]:
        all_permissions = set()
        for role in self.roles:
            all_permissions.add(role.get_all_permissions())
        return all_permissions

    def is_allowed(self, query: str) -> bool:
        return any(role.is_allowed(query) for role in self.roles)
