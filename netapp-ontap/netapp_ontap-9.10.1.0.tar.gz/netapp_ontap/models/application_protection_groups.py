r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationProtectionGroups", "ApplicationProtectionGroupsSchema"]
__pdoc__ = {
    "ApplicationProtectionGroupsSchema.resource": False,
    "ApplicationProtectionGroups": False,
}


class ApplicationProtectionGroupsSchema(ResourceSchema):
    """The fields of the ApplicationProtectionGroups object"""

    name = fields.Str(data_key="name")
    r""" Protection group name """

    rpo = fields.Nested("netapp_ontap.models.application_protection_groups_rpo.ApplicationProtectionGroupsRpoSchema", unknown=EXCLUDE, data_key="rpo")
    r""" The rpo field of the application_protection_groups. """

    uuid = fields.Str(data_key="uuid")
    r""" Protection group UUID """

    @property
    def resource(self):
        return ApplicationProtectionGroups

    gettable_fields = [
        "name",
        "rpo",
        "uuid",
    ]
    """name,rpo,uuid,"""

    patchable_fields = [
        "rpo",
    ]
    """rpo,"""

    postable_fields = [
        "rpo",
    ]
    """rpo,"""


class ApplicationProtectionGroups(Resource):

    _schema = ApplicationProtectionGroupsSchema
