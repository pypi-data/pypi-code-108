from typing import Optional, Type, Dict

from .list import List
from .membership import Membership


class MembershipList(List):
    def get_memberships_of_types(self, class_):
        return list(
            filter(
                lambda membership: isinstance(membership.resource_group, class_),
                self._items
            )
        )

    def get_membership_by_resource_group_id(self, resource_group_id: str) -> Membership:
        for membership in self._items:
            if membership.resource_group.resource_group_id == resource_group_id:
                return membership
        return None

    def get_membership_by_name(self, name: str) -> Membership:
        for membership in self._items:
            if membership.resource_group.name == name:
                return membership
        return None

    def get_memberships(self,
                        tenant_id: Optional[str] = None,
                        type_: Optional[str] = None) -> List[Membership]:
        memberships = self._items
        if tenant_id:
            memberships = filter(
                lambda membership: membership.resource_group.tenant_id == tenant_id,
                memberships
            )

        if type_:
            from .resource_group.club import ClubResourceGroup
            from .resource_group.team import TeamResourceGroup

            class_map: Dict[str, Type] = {
                'team': TeamResourceGroup,
                'club': ClubResourceGroup
            }
            class_ = class_map[type_]

            memberships = filter(
                lambda membership: isinstance(membership.resource_group, class_),
                memberships
            )

        return list(memberships)
