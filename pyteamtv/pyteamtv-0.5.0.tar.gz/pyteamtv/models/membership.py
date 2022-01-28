from .teamtv_object import TeamTVObject
from .resource_group.factory import factory as resource_group_factory


class Membership(TeamTVObject):
    @property
    def role_names(self):
        return self._role_names

    @property
    def resource_group(self):
        return self._resource_group

    @property
    def member_attributes(self):
        return self._member_attributes

    def _use_attributes(self, attributes: dict):
        self._role_names = attributes['roleNames']
        self._member_attributes = attributes['memberAttributes']

        self._resource_group = resource_group_factory(
            self._requester,
            dict(
                tenantId=attributes['tenantId'],
                resourceGroupId=attributes['resourceGroupId'],
                targetResourceId=attributes['targetResourceId'],
                targetResourceName=attributes['targetResourceName']
            )
        )

    def __repr__(self):
        return f"<Membership resourceGroup={self.resource_group} role={self.role_names[0]}>"
