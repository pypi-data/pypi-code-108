r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationCifsPropertiesPermissions", "ApplicationCifsPropertiesPermissionsSchema"]
__pdoc__ = {
    "ApplicationCifsPropertiesPermissionsSchema.resource": False,
    "ApplicationCifsPropertiesPermissions": False,
}


class ApplicationCifsPropertiesPermissionsSchema(ResourceSchema):
    """The fields of the ApplicationCifsPropertiesPermissions object"""

    access = fields.Str(data_key="access")
    r""" Access granted to the user or group """

    user_or_group = fields.Str(data_key="user_or_group")
    r""" User or group """

    @property
    def resource(self):
        return ApplicationCifsPropertiesPermissions

    gettable_fields = [
        "access",
        "user_or_group",
    ]
    """access,user_or_group,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationCifsPropertiesPermissions(Resource):

    _schema = ApplicationCifsPropertiesPermissionsSchema
