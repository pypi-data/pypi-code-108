from .teamtv_object import TeamTVObject


class SharingGroup(TeamTVObject):
    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def visibility_type(self):
        return self._visibility_type

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def sharing_group_id(self):
        return self._sharing_group_id

    @property
    def attributes(self):
        return self._attributes

    def _use_attributes(self, attributes: dict):
        self._name = attributes['name']
        self._description = attributes['description']
        self._visibility_type = attributes['visibilityType']
        self._tenant_id = attributes['tenantId']
        self._sharing_group_id = attributes['sharingGroupId']
        self._attributes = attributes['attributes']
