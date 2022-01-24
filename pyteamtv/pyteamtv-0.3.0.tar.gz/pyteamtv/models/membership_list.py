from typing import Optional

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

